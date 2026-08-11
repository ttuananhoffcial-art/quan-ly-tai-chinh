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
    // KHỞI TẠO BẢNG CSDL D1
    await env.DB.exec(`
      CREATE TABLE IF NOT EXISTS sys_users (id TEXT PRIMARY KEY, phone TEXT, data TEXT);
      CREATE TABLE IF NOT EXISTS work_projects (id TEXT PRIMARY KEY, user_id TEXT, data TEXT);
      CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, user_id TEXT, type TEXT, category TEXT, amount REAL, note TEXT, date TEXT);
      CREATE TABLE IF NOT EXISTS debts (id TEXT PRIMARY KEY, user_id TEXT, person_name TEXT, debt_type TEXT, amount REAL, status TEXT, date TEXT);
    `);

    // A. XỬ LÝ XÓA TÀI KHOẢN TỨC THÌ TRÊN D1 (NGẮN CHẶN BỊ HỒI SINH)
    if (request.method === "POST" && action === "delete-user") {
      const body = await request.json();
      const { targetId, targetPhone } = body;
      const stmts = [];

      if (targetId) stmts.push(env.DB.prepare("DELETE FROM sys_users WHERE id = ?").bind(String(targetId)));
      if (targetPhone) stmts.push(env.DB.prepare("DELETE FROM sys_users WHERE phone = ?").bind(String(targetPhone)));

      if (stmts.length > 0) {
        await env.DB.batch(stmts);
      }
      return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
    }

    // B. XỬ LÝ ĐĂNG KÝ TÀI KHOẢN MỚI TRỰC TIẾP
    if (request.method === "POST" && action === "register-user") {
      const body = await request.json();
      const { user } = body;

      if (user && user.id && user.phone && user.username) {
        await env.DB.prepare("DELETE FROM sys_users WHERE id = ? OR phone = ?").bind(String(user.id), String(user.phone)).run();
        await env.DB.prepare("INSERT INTO sys_users (id, phone, data) VALUES (?, ?, ?)").bind(String(user.id), String(user.phone), JSON.stringify(user)).run();
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }
      return new Response(JSON.stringify({ error: "Invalid user data" }), { status: 400, headers: corsHeaders });
    }

    // C. ĐỒNG BỘ DỮ LIỆU TỰ ĐỘNG LÊN SERVER
    if (request.method === "POST" && action === "sync-data") {
      const body = await request.json();
      const { userId, users, workProjects, transactions, debts, deletedProjectIds, deletedTransIds } = body;

      const stmts = [];

      if (deletedProjectIds && Array.isArray(deletedProjectIds)) {
        for (let pId of deletedProjectIds) {
          if (pId) {
            stmts.push(env.DB.prepare("DELETE FROM work_projects WHERE id = ?").bind(String(pId)));
          }
        }
      }

      if (deletedTransIds && Array.isArray(deletedTransIds)) {
        for (let tId of deletedTransIds) {
          if (tId) {
            stmts.push(env.DB.prepare("DELETE FROM transactions WHERE id = ?").bind(String(tId)));
          }
        }
      }

      // CHỈ CẬP NHẬT TÀI KHOẢN KHI ĐƯỢC TRUYỀN TỪ MÁY ADMIN
      if (users && Array.isArray(users)) {
        for (let u of users) {
          if (u && u.id && u.phone && u.username) {
            stmts.push(env.DB.prepare("DELETE FROM sys_users WHERE id = ? OR phone = ?").bind(String(u.id), String(u.phone)));
            stmts.push(
              env.DB.prepare("INSERT INTO sys_users (id, phone, data) VALUES (?, ?, ?)").bind(String(u.id), String(u.phone), JSON.stringify(u))
            );
          }
        }
      }

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

      if (stmts.length > 0) {
        for (let i = 0; i < stmts.length; i += 50) {
          const chunk = stmts.slice(i, i + 50);
          await env.DB.batch(chunk);
        }
      }

      return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
    }

    // D. TẢI DỮ LIỆU TỪ SERVER VỀ
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
        try { 
          const parsed = JSON.parse(u.data);
          return (parsed && parsed.phone && parsed.username) ? parsed : null;
        } catch(e) { return null; }
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