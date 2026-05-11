export type Bucket = "risk" | "disposal" | "exiting";

export interface Stock {
  code: string;
  name: string;
  market: "TWSE" | "TPEx";
  bucket: Bucket;
  industry: string | null;
  close: number | null;
  change: number | null;
  change_pct: number | null;
  value_100m: number | null;
  can_intraday: boolean;
  notice_count_30d: number;
  measure: string | null;
  auction_minutes: number | null;
  prepay_full: boolean;
  period_start: string | null;
  period_end: string | null;
  condition: string | null;
}

export interface Snapshot {
  updated_at: string;
  trading_day: string;
  risk: Stock[];
  disposal: Stock[];
  exiting: Stock[];
}
