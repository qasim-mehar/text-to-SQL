export interface GenerateRequest {
  question: string
}

export interface GenerateResponse {
  sql: string
  success: boolean
  retry_count?: number
}

export interface ExecuteRequest {
  sql: string
}

export interface ExecuteResponse {
  columns: string[]
  rows: Record<string, unknown>[]
  row_count: number
  execution_time_ms: number
}

export interface ColumnInfo {
  name: string
  type: string
}

export interface ForeignKeyInfo {
  from_col: string
  to_table: string
  to_column: string
}

export interface TableInfo {
  name: string
  columns: ColumnInfo[]
  foreign_keys: ForeignKeyInfo[]
}

export interface SchemaResponse {
  tables: TableInfo[]
}

export interface QueryHistoryItem {
  id: string
  question: string
  sql: string
  timestamp: number
  row_count?: number
}
