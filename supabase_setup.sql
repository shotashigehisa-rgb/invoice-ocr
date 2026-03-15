-- Supabaseのダッシュボード > SQL Editor で実行してください

CREATE TABLE invoices (
  id         uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now(),
  recipient  text,
  date       text,
  amount     text
);
