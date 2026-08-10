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
    // 1. ĐỒNG BỘ DỮ LIỆU LÊN CLOUDFLARE D1 (CHIA GÓI 50 CÂU LỆNH CHỐNG LỖI BATCH LIMIT)
    if (request.method === "POST" && action === "sync-data") {
      const body = await request.json();
      const { userId, transactions, debts } = body;

      if (userId) {
        const stmts = [];
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

        // CHIA NHỎ MỖI LẦN GỬI 50 CÂU LỆNH ĐỂ KHÔNG BỊ TRÌNH DUYỆT / D1 HỦY
        for (let i = 0; i < stmts.length; i += 50) {
          const chunk = stmts.slice(i, i + 50);
          await env.DB.batch(chunk);
        }
      }

      return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
    }

    // 2. TẢI DỮ LIỆU ĐÁM MÂY VỀ THIẾT BỊ
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

      return new Response(JSON.stringify({ transactions: formattedTrans, debts: formattedDebts }), { headers: corsHeaders });
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
  }

  return new Response("Not found", { status: 404, headers: corsHeaders });
}