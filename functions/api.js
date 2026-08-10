export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const action = url.searchParams.get("action");

  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache, no-store, must-revalidate"
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // TỰ ĐỘNG TẠO BẢNG CHỨA MÃ CÔNG VIỆC VÀ TÀI KHOẢN PHỤ TRÊN CLOUDFLARE D1
    await env.DB.exec(`
      CREATE TABLE IF NOT EXISTS work_projects (id TEXT PRIMARY KEY, user_id TEXT, data TEXT);
      CREATE TABLE IF NOT EXISTS sys_users (id TEXT PRIMARY KEY, phone TEXT, data TEXT);
    `);

    // 1. LƯU & ĐỒNG BỘ TOÀN BỘ TÀI KHOẢN, MÃ CÔNG VIỆC, GIAO DỊCH, NỢ LEÊN CLOUD
    if (request.method === "POST" && action === "sync-data") {
      const body = await request.json();
      const { userId, users, workProjects, transactions, debts } = body;

      const stmts = [];

      // Lưu danh sách Tài khoản (bao gồm Tài khoản phụ & Quyền hạn)
      if (users && Array.isArray(users)) {
        for (let u of users) {
          stmts.push(
            env.DB.prepare(
              "INSERT INTO sys_users (id, phone, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET phone=excluded.phone, data=excluded.data"
            ).bind(String(u.id), String(u.phone), JSON.stringify(u))
          );
        }
      }

      // Lưu danh sách Mã Công Việc
      if (workProjects && Array.isArray(workProjects)) {
        for (let p of workProjects) {
          stmts.push(
            env.DB.prepare(
              "INSERT INTO work_projects (id, user_id, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET data=excluded.data"
            ).bind(String(p.id), String(p.userId || userId), JSON.stringify(p))
          );
        }
      }

      // Lưu Giao dịch & Khoản nợ
      if (userId) {
        stmts.push(env.DB.prepare("DELETE FROM transactions WHERE user_id = ?").bind(String(userId)));
        stmts.push(env.DB.prepare("DELETE FROM debts WHERE user_id = ?").bind(String(userId)));

        if (transactions && Array.isArray(transactions)) {
          for (let t of transactions) {
            stmts.push(
              env.DB.prepare(
                "INSERT INTO transactions (id, user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?, ?)"
              ).bind(
                String(t.id),
                String(t.userId || userId),
                String(t.type || ''),
                String(t.category || ''),
                Number(t.amount) || 0,
                String(t.note || ''),
                String(t.date || '')
              )
            );
          }
        }

        if (debts && Array.isArray(debts)) {
          for (let d of debts) {
            stmts.push(
              env.DB.prepare(
                "INSERT INTO debts (id, user_id, person_name, debt_type, amount, status, date) VALUES (?, ?, ?, ?, ?, ?, ?)"
              ).bind(
                String(d.id),
                String(d.userId || userId),
                String(d.personName || ''),
                String(d.debtType || ''),
                Number(d.amount) || 0,
                String(d.status || ''),
                String(d.date || '')
              )
            );
          }
        }
      }

      // Gửi dữ liệu theo từng gói 50 câu lệnh
      for (let i = 0; i < stmts.length; i += 50) {
        const chunk = stmts.slice(i, i + 50);
        await env.DB.batch(chunk);
      }

      return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
    }

    // 2. TẢI TOÀN BỘ TÀI KHOẢN, MÃ CÔNG VIỆC, GIAO DỊCH, NỢ VỀ THIẾT BỊ
    if (request.method === "GET" && action === "get-data") {
      const trans = await env.DB.prepare("SELECT * FROM transactions").all();
      const debts = await env.DB.prepare("SELECT * FROM debts").all();
      const dbUsers = await env.DB.prepare("SELECT * FROM sys_users").all();
      const dbProjects = await env.DB.prepare("SELECT * FROM work_projects").all();

      const formattedTrans = (trans.results || []).map(t => ({
        id: t.id,
        userId: t.user_id,
        type: t.type,
        category: t.category,
        amount: t.amount,
        note: t.note,
        date: t.date
      }));

      const formattedDebts = (debts.results || []).map(d => ({
        id: d.id,
        userId: d.user_id,
        personName: d.person_name,
        debtType: d.debt_type,
        amount: d.amount,
        status: d.status,
        date: d.date
      }));

      const formattedUsers = (dbUsers.results || []).map(u => {
        try { return JSON.parse(u.data); } catch(e) { return null; }
      }).filter(u => u !== null);

      const formattedProjects = (dbProjects.results || []).map(p => {
        try { return JSON.parse(p.data); } catch(e) { return null; }
      }).filter(p => p !== null);

      return new Response(JSON.stringify({
        transactions: formattedTrans,
        debts: formattedDebts,
        users: formattedUsers,
        workProjects: formattedProjects
      }), { headers: corsHeaders });
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
  }

  return new Response("Not found", { status: 404, headers: corsHeaders });
}