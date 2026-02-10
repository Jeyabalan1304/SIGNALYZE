export interface ClassifiedInsight {
  id: string;
  item_id: string;
  item_type: string;
  product_category: string;
  product_subcategory: string;
  make_brand: string;
  model: string;
  variant: string;
  color: string;
  size_capacity: string;
  configuration: string;
  release_year: number | null;
  price_band: string;
  market_segment: string;
  verified_purchase: boolean;
  purchase_channel: string;
  purchase_region: string;
  usage_duration_bucket: string;
  ownership_stage: string;
  disposition_1: string;
  disposition_2: string;
  disposition_3: string;
  disposition_4: string;
  disposition_5: string;
  created_at: string;
  // Raw text is usually joined from preprocessed table
  raw_text?: string;
}

export interface DashboardStats {
  total_feedback: number;
  classified_signal: number;
  pending_processing: number;
}

export interface ChartData {
  name: string;
  value: number;
}

export interface DashboardCharts {
  sentiment: ChartData[];
  area: ChartData[];
}
