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
    // TỰ ĐỘNG KHỞI TẠO CÁC BẢNG CSDL TRÊN CLOUDFLARE D1
    await env.DB.exec(`
      CREATE TABLE IF NOT EXISTS sys_users (id TEXT PRIMARY KEY, phone TEXT, data TEXT);
      CREATE TABLE IF NOT EXISTS work_projects (id TEXT PRIMARY KEY, user_id TEXT, data TEXT);
      CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, user_id TEXT, type TEXT, category TEXT, amount REAL, note TEXT, date TEXT);
      CREATE TABLE IF NOT EXISTS debts (id TEXT PRIMARY KEY, user_id TEXT, person_name TEXT, debt_type TEXT, amount REAL, status TEXT, date TEXT);
    `);

    // 1. ĐỒNG BỘ DỮ LIỆU TỪ CÁC THIẾT BỊ LÊN SERVER
    if (request.method === "POST" && action === "sync-data") {
      const body = await request.json();
      const { userId, users, workProjects, transactions, debts, deletedUserIds, deletedProjectIds, deletedTransIds } = body;

      const stmts = [];

      // A. XÓA VĨNH VIỄN TÀI KHOẢN KHỎI CSDL KHI ADMIN XÓA
      if (deletedUserIds && Array.isArray(deletedUserIds)) {
        for (let delId of deletedUserIds) {
          if (delId) {
            stmts.push(env.DB.prepare("DELETE FROM sys_users WHERE id = ? OR phone = ?").bind(String(delId), String(delId)));
          }
        }
      }

      // B. XÓA MÃ CÔNG VIỆC KHỎI D1
      if (deletedProjectIds && Array.isArray(deletedProjectIds)) {
        for (let pId of deletedProjectIds) {
          if (pId) {
            stmts.push(env.DB.prepare("DELETE FROM work_projects WHERE id = ?").bind(String(pId)));
          }
        }
      }

      // C. XÓA GIAO DỊCH KHỎI D1
      if (deletedTransIds && Array.isArray(deletedTransIds)) {
        for (let tId of deletedTransIds) {
          if (tId) {
            stmts.push(env.DB.prepare("DELETE FROM transactions WHERE id = ?").bind(String(tId)));
          }
        }
      }

      // D. LƯU & CẬP NHẬT TÀI KHOẢN ĐĂNG KÝ MỚI LÊN DATABASE D1
      if (users && Array.isArray(users)) {
        for (let u of users) {
          if (u && u.id && u.phone) {
            stmts.push(env.DB.prepare("DELETE FROM sys_users WHERE id = ? OR phone = ?").bind(String(u.id), String(u.phone)));
            stmts.push(
              env.DB.prepare("INSERT INTO sys_users (id, phone, data) VALUES (?, ?, ?)").bind(String(u.id), String(u.phone), JSON.stringify(u))
            );
          }
        }
      }

      // E. LƯU CÔNG VIỆC MỚI
      if (workProjects && Array.isArray(workProjects)) {
        for (let p of workProjects) {
          if (p && p.id) {
            stmts.push(env.DB.prepare("DELETE FROM work_projects WHERE id = ?").bind(String(p.id)));
            stmts.push(
              env.DB.prepare("INSERT INTO work_projects (id, user_id, data) VALUES (?, ?, ?)").bind(String(p.id), String(p.userId || userId || ''), JSON.stringify(p))
            );
          }
        }
      }

      // F. LƯU GIAO DỊCH VÀ NỢ CỦA TÀI KHOẢN
      if (userId && userId !== 'guest') {
        stmts.push(env.DB.prepare("DELETE FROM transactions WHERE user_id = ?").bind(String(userId)));
        stmts.push(env.DB.prepare("DELETE FROM debts WHERE user_id = ?").bind(String(userId)));

        if (transactions && Array.isArray(transactions)) {
          for (let t of transactions) {
            if (t && t.id) {
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
        }

        if (debts && Array.isArray(debts)) {
          for (let d of debts) {
            if (d && d.id) {
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
      }

      // THỰC THI TOÀN BỘ CÂU LỆNH SQL THEO GÓI 50 LỆNH
      if (stmts.length > 0) {
        for (let i = 0; i < stmts.length; i += 50) {
          const chunk = stmts.slice(i, i + 50);
          await env.DB.batch(chunk);
        }
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