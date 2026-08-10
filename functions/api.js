export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const action = url.searchParams.get("action");

  // 1. ĐỒNG BỘ DỮ LIỆU TỪ THIẾT BỊ LÊN CLOUDFLARE D1
  if (request.method === "POST" && action === "sync-data") {
    try {
      const body = await request.json();
      const { userId, transactions, debts } = body;

      if (userId) {
        // Xóa dữ liệu cũ của user để ghi đè bản mới nhất
        await env.DB.prepare("DELETE FROM transactions WHERE user_id = ?").bind(String(userId)).run();
        await env.DB.prepare("DELETE FROM debts WHERE user_id = ?").bind(String(userId)).run();

        // Ghi lại danh sách giao dịch
        if (transactions && Array.isArray(transactions)) {
          for (let t of transactions) {
            await env.DB.prepare(
              "INSERT INTO transactions (id, user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?, ?)"
            ).bind(
              String(t.id),
              String(t.userId || userId),
              String(t.type || ''),
              String(t.category || ''),
              Number(t.amount) || 0,
              String(t.note || ''),
              String(t.date || '')
            ).run();
          }
        }

        // Ghi lại danh sách khoản nợ
        if (debts && Array.isArray(debts)) {
          for (let d of debts) {
            await env.DB.prepare(
              "INSERT INTO debts (id, user_id, person_name, debt_type, amount, status, date) VALUES (?, ?, ?, ?, ?, ?, ?)"
            ).bind(
              String(d.id),
              String(d.userId || userId),
              String(d.personName || ''),
              String(d.debtType || ''),
              Number(d.amount) || 0,
              String(d.status || ''),
              String(d.date || '')
            ).run();
          }
        }
      }

      return new Response(JSON.stringify({ success: true }), {
        headers: { "Content-Type": "application/json" }
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), { status: 500 });
    }
  }

  // 2. LẤY TOÀN BỘ DỮ LIỆU ĐÁM MÂY VỀ THIẾT BỊ
  if (request.method === "GET" && action === "get-data") {
    try {
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

      return new Response(JSON.stringify({ transactions: formattedTrans, debts: formattedDebts }), {
        headers: { "Content-Type": "application/json" }
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), { status: 500 });
    }
  }

  return new Response("Not found", { status: 404 });
}