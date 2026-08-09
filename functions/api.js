export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const action = url.searchParams.get("action");

  // 1. ĐỒNG BỘ DỮ LIỆU TỪ THIẾT BỊ LÊN CLOUDFLARE D1
  if (request.method === "POST" && action === "sync-data") {
    const body = await request.json();
    const { userId, users, workProjects, transactions, debts } = body;

    // Lưu / Cập nhật Danh sách Tài khoản
    if (users && users.length > 0) {
      for (let u of users) {
        await env.DB.prepare(
          "INSERT INTO users (id, phone, username, password) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET username=excluded.username, password=excluded.password"
        ).bind(String(u.id), String(u.phone), String(u.username), String(u.password)).run();
      }
    }

    // Làm sạch và ghi đè giao dịch + khoản nợ
    if (userId) {
      await env.DB.prepare("DELETE FROM transactions WHERE user_id = ?").bind(String(userId)).run();
      await env.DB.prepare("DELETE FROM debts WHERE user_id = ?").bind(String(userId)).run();

      for (let t of transactions) {
        await env.DB.prepare("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)").bind(
          String(t.id), String(t.userId || userId), t.type || '', t.category || '', Number(t.amount) || 0, t.note || '', t.date || ''
        ).run();
      }
      for (let d of debts) {
        await env.DB.prepare("INSERT INTO debts VALUES (?, ?, ?, ?, ?, ?, ?)").bind(
          String(d.id), String(d.userId || userId), d.personName || '', d.debtType || '', Number(d.amount) || 0, d.status || '', d.date || ''
        ).run();
      }
    }

    return new Response(JSON.stringify({ success: true }));
  }

  // 2. TẢI DỮ LIỆU TOÀN BỘ HỆ THỐNG VỀ ĐỂ ĐỒNG BỘ TỨC THỜI
  if (request.method === "GET" && action === "get-data") {
    const trans = await env.DB.prepare("SELECT * FROM transactions").all();
    const debts = await env.DB.prepare("SELECT * FROM debts").all();

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

    return new Response(JSON.stringify({ transactions: formattedTrans, debts: formattedDebts }));
  }

  return new Response("Not found", { status: 404 });
}