export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      accounts: {
        Row: {
          account_number_masked: string | null
          account_type: string
          created_at: string | null
          currency: string | null
          id: string
          institution_id: string
          is_active: boolean | null
          name: string
        }
        Insert: {
          account_number_masked?: string | null
          account_type: string
          created_at?: string | null
          currency?: string | null
          id?: string
          institution_id: string
          is_active?: boolean | null
          name: string
        }
        Update: {
          account_number_masked?: string | null
          account_type?: string
          created_at?: string | null
          currency?: string | null
          id?: string
          institution_id?: string
          is_active?: boolean | null
          name?: string
        }
        Relationships: [
          {
            foreignKeyName: "accounts_institution_id_fkey"
            columns: ["institution_id"]
            isOneToOne: false
            referencedRelation: "institutions"
            referencedColumns: ["id"]
          },
        ]
      }
      categories: {
        Row: {
          color: string | null
          created_at: string | null
          icon: string | null
          id: string
          name: string
          parent_id: string | null
        }
        Insert: {
          color?: string | null
          created_at?: string | null
          icon?: string | null
          id?: string
          name: string
          parent_id?: string | null
        }
        Update: {
          color?: string | null
          created_at?: string | null
          icon?: string | null
          id?: string
          name?: string
          parent_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "categories_parent_id_fkey"
            columns: ["parent_id"]
            isOneToOne: false
            referencedRelation: "categories"
            referencedColumns: ["id"]
          },
        ]
      }
      holdings: {
        Row: {
          account_id: string
          as_of_date: string
          cost_basis: number | null
          created_at: string | null
          id: string
          quantity: number
          symbol: string
        }
        Insert: {
          account_id: string
          as_of_date: string
          cost_basis?: number | null
          created_at?: string | null
          id?: string
          quantity: number
          symbol: string
        }
        Update: {
          account_id?: string
          as_of_date?: string
          cost_basis?: number | null
          created_at?: string | null
          id?: string
          quantity?: number
          symbol?: string
        }
        Relationships: [
          {
            foreignKeyName: "holdings_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      institutions: {
        Row: {
          created_at: string | null
          id: string
          name: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          name: string
        }
        Update: {
          created_at?: string | null
          id?: string
          name?: string
        }
        Relationships: []
      }
      merchant_cache: {
        Row: {
          category: string
          confidence: number | null
          created_at: string | null
          id: string
          normalized_merchant: string
          raw_store: string
          source: string | null
          sub_category: string | null
          updated_at: string | null
        }
        Insert: {
          category: string
          confidence?: number | null
          created_at?: string | null
          id?: string
          normalized_merchant: string
          raw_store: string
          source?: string | null
          sub_category?: string | null
          updated_at?: string | null
        }
        Update: {
          category?: string
          confidence?: number | null
          created_at?: string | null
          id?: string
          normalized_merchant?: string
          raw_store?: string
          source?: string | null
          sub_category?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      receipt_items: {
        Row: {
          category: string | null
          created_at: string | null
          id: string
          item_name: string | null
          item_name_raw: string | null
          line_total: number
          quantity: number | null
          receipt_id: string
          sort_order: number | null
          sub_category: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          id?: string
          item_name?: string | null
          item_name_raw?: string | null
          line_total: number
          quantity?: number | null
          receipt_id: string
          sort_order?: number | null
          sub_category?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          id?: string
          item_name?: string | null
          item_name_raw?: string | null
          line_total?: number
          quantity?: number | null
          receipt_id?: string
          sort_order?: number | null
          sub_category?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "receipt_items_receipt_id_fkey"
            columns: ["receipt_id"]
            isOneToOne: false
            referencedRelation: "receipts"
            referencedColumns: ["id"]
          },
        ]
      }
      receipt_transactions: {
        Row: {
          amount_attributed: number | null
          created_at: string | null
          id: string
          receipt_id: string
          transaction_id: string
        }
        Insert: {
          amount_attributed?: number | null
          created_at?: string | null
          id?: string
          receipt_id: string
          transaction_id: string
        }
        Update: {
          amount_attributed?: number | null
          created_at?: string | null
          id?: string
          receipt_id?: string
          transaction_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "receipt_transactions_receipt_id_fkey"
            columns: ["receipt_id"]
            isOneToOne: false
            referencedRelation: "receipts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "receipt_transactions_transaction_id_fkey"
            columns: ["transaction_id"]
            isOneToOne: true
            referencedRelation: "transactions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "receipt_transactions_transaction_id_fkey"
            columns: ["transaction_id"]
            isOneToOne: true
            referencedRelation: "transfer_summary"
            referencedColumns: ["transaction_id"]
          },
        ]
      }
      receipts: {
        Row: {
          account_id: string
          created_at: string | null
          currency: string | null
          discount_amount: number | null
          id: string
          image_path: string
          match_status: string
          merchant_name: string | null
          ocr_raw_text: string | null
          ocr_structured_json: Json | null
          payment_method_raw: string | null
          processing_status: string
          receipt_date: string | null
          receipt_time: string | null
          store_address: string | null
          subtotal: number | null
          tax_amount: number | null
          tip_amount: number | null
          total: number | null
          updated_at: string | null
        }
        Insert: {
          account_id: string
          created_at?: string | null
          currency?: string | null
          discount_amount?: number | null
          id?: string
          image_path: string
          match_status?: string
          merchant_name?: string | null
          ocr_raw_text?: string | null
          ocr_structured_json?: Json | null
          payment_method_raw?: string | null
          processing_status?: string
          receipt_date?: string | null
          receipt_time?: string | null
          store_address?: string | null
          subtotal?: number | null
          tax_amount?: number | null
          tip_amount?: number | null
          total?: number | null
          updated_at?: string | null
        }
        Update: {
          account_id?: string
          created_at?: string | null
          currency?: string | null
          discount_amount?: number | null
          id?: string
          image_path?: string
          match_status?: string
          merchant_name?: string | null
          ocr_raw_text?: string | null
          ocr_structured_json?: Json | null
          payment_method_raw?: string | null
          processing_status?: string
          receipt_date?: string | null
          receipt_time?: string | null
          store_address?: string | null
          subtotal?: number | null
          tax_amount?: number | null
          tip_amount?: number | null
          total?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "receipts_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      statements: {
        Row: {
          account_id: string
          closing_balance: number | null
          confidence: number | null
          file_name: string
          id: string
          imported_at: string | null
          month: number
          opening_balance: number | null
          total_credits: number | null
          total_debits: number | null
          transaction_count: number | null
          year: number
        }
        Insert: {
          account_id: string
          closing_balance?: number | null
          confidence?: number | null
          file_name: string
          id?: string
          imported_at?: string | null
          month: number
          opening_balance?: number | null
          total_credits?: number | null
          total_debits?: number | null
          transaction_count?: number | null
          year: number
        }
        Update: {
          account_id?: string
          closing_balance?: number | null
          confidence?: number | null
          file_name?: string
          id?: string
          imported_at?: string | null
          month?: number
          opening_balance?: number | null
          total_credits?: number | null
          total_debits?: number | null
          transaction_count?: number | null
          year?: number
        }
        Relationships: [
          {
            foreignKeyName: "statements_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      subscriptions: {
        Row: {
          billing_day: number | null
          category: string | null
          confidence: number | null
          created_at: string | null
          current_amount: number | null
          description: string | null
          ended_at: string | null
          frequency: string
          id: string
          is_active: boolean | null
          last_charged_at: string
          merchant: string
          next_expected_at: string | null
          notes: string | null
          started_at: string
          status: string | null
          updated_at: string | null
        }
        Insert: {
          billing_day?: number | null
          category?: string | null
          confidence?: number | null
          created_at?: string | null
          current_amount?: number | null
          description?: string | null
          ended_at?: string | null
          frequency: string
          id?: string
          is_active?: boolean | null
          last_charged_at: string
          merchant: string
          next_expected_at?: string | null
          notes?: string | null
          started_at: string
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          billing_day?: number | null
          category?: string | null
          confidence?: number | null
          created_at?: string | null
          current_amount?: number | null
          description?: string | null
          ended_at?: string | null
          frequency?: string
          id?: string
          is_active?: boolean | null
          last_charged_at?: string
          merchant?: string
          next_expected_at?: string | null
          notes?: string | null
          started_at?: string
          status?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      trade_details: {
        Row: {
          created_at: string | null
          currency: string | null
          fx_rate: number | null
          id: string
          quantity: number | null
          symbol: string
          transaction_id: string
          unit_price: number | null
        }
        Insert: {
          created_at?: string | null
          currency?: string | null
          fx_rate?: number | null
          id?: string
          quantity?: number | null
          symbol: string
          transaction_id: string
          unit_price?: number | null
        }
        Update: {
          created_at?: string | null
          currency?: string | null
          fx_rate?: number | null
          id?: string
          quantity?: number | null
          symbol?: string
          transaction_id?: string
          unit_price?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "trade_details_transaction_id_fkey"
            columns: ["transaction_id"]
            isOneToOne: true
            referencedRelation: "transactions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "trade_details_transaction_id_fkey"
            columns: ["transaction_id"]
            isOneToOne: true
            referencedRelation: "transfer_summary"
            referencedColumns: ["transaction_id"]
          },
        ]
      }
      transactions: {
        Row: {
          account_id: string
          activity_type: string | null
          amount: number
          balance: number | null
          category: string | null
          created_at: string | null
          date: string
          description: string
          has_receipt: boolean | null
          id: string
          linked_transaction_id: string | null
          location: string | null
          merchant: string | null
          raw_data: Json | null
          raw_text: string | null
          source_file: string | null
          source_hash: string | null
          sub_category: string | null
          subscription_id: string | null
          transaction_type: string
        }
        Insert: {
          account_id: string
          activity_type?: string | null
          amount: number
          balance?: number | null
          category?: string | null
          created_at?: string | null
          date: string
          description: string
          has_receipt?: boolean | null
          id?: string
          linked_transaction_id?: string | null
          location?: string | null
          merchant?: string | null
          raw_data?: Json | null
          raw_text?: string | null
          source_file?: string | null
          source_hash?: string | null
          sub_category?: string | null
          subscription_id?: string | null
          transaction_type: string
        }
        Update: {
          account_id?: string
          activity_type?: string | null
          amount?: number
          balance?: number | null
          category?: string | null
          created_at?: string | null
          date?: string
          description?: string
          has_receipt?: boolean | null
          id?: string
          linked_transaction_id?: string | null
          location?: string | null
          merchant?: string | null
          raw_data?: Json | null
          raw_text?: string | null
          source_file?: string | null
          source_hash?: string | null
          sub_category?: string | null
          subscription_id?: string | null
          transaction_type?: string
        }
        Relationships: [
          {
            foreignKeyName: "transactions_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "accounts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "transactions_linked_transaction_id_fkey"
            columns: ["linked_transaction_id"]
            isOneToOne: false
            referencedRelation: "transactions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "transactions_linked_transaction_id_fkey"
            columns: ["linked_transaction_id"]
            isOneToOne: false
            referencedRelation: "transfer_summary"
            referencedColumns: ["transaction_id"]
          },
          {
            foreignKeyName: "transactions_subscription_id_fkey"
            columns: ["subscription_id"]
            isOneToOne: false
            referencedRelation: "active_subscriptions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "transactions_subscription_id_fkey"
            columns: ["subscription_id"]
            isOneToOne: false
            referencedRelation: "subscription_history"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "transactions_subscription_id_fkey"
            columns: ["subscription_id"]
            isOneToOne: false
            referencedRelation: "subscriptions"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      active_subscriptions: {
        Row: {
          billing_day: number | null
          category: string | null
          charge_count: number | null
          confidence: number | null
          current_amount: number | null
          description: string | null
          frequency: string | null
          id: string | null
          last_charged_at: string | null
          merchant: string | null
          next_expected_at: string | null
          started_at: string | null
          status: string | null
          total_spent: number | null
        }
        Relationships: []
      }
      category_trends: {
        Row: {
          absolute_change: number | null
          category: string | null
          current_spent: number | null
          month: string | null
          pct_change: number | null
          previous_spent: number | null
          transaction_count: number | null
        }
        Relationships: []
      }
      current_holdings: {
        Row: {
          account_id: string | null
          account_name: string | null
          as_of_date: string | null
          cost_basis: number | null
          institution: string | null
          quantity: number | null
          symbol: string | null
        }
        Relationships: [
          {
            foreignKeyName: "holdings_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      investment_activity: {
        Row: {
          account_name: string | null
          activity_type: string | null
          symbol: string | null
          total_quantity: number | null
          total_value: number | null
          trade_count: number | null
        }
        Relationships: []
      }
      merchant_summary: {
        Row: {
          avg_amount: number | null
          category: string | null
          first_seen: string | null
          last_seen: string | null
          merchant_name: string | null
          total_spent: number | null
          transaction_count: number | null
        }
        Relationships: []
      }
      monthly_spending_by_account: {
        Row: {
          account_name: string | null
          account_type: string | null
          month: string | null
          net: number | null
          received: number | null
          spent: number | null
          transaction_count: number | null
        }
        Relationships: []
      }
      monthly_spending_by_category: {
        Row: {
          avg_transaction: number | null
          category: string | null
          month: string | null
          received: number | null
          spent: number | null
          transaction_count: number | null
        }
        Relationships: []
      }
      monthly_subscription_cost: {
        Row: {
          active_count: number | null
          monthly_total: number | null
        }
        Relationships: []
      }
      net_worth_timeline: {
        Row: {
          accounts_with_data: number | null
          date: string | null
          net_worth: number | null
        }
        Relationships: []
      }
      subscription_history: {
        Row: {
          category: string | null
          charge_count: number | null
          confidence: number | null
          current_amount: number | null
          description: string | null
          ended_at: string | null
          frequency: string | null
          id: string | null
          is_active: boolean | null
          last_charged_at: string | null
          max_amount: number | null
          merchant: string | null
          min_amount: number | null
          months_active: number | null
          started_at: string | null
          status: string | null
          total_spent: number | null
        }
        Relationships: []
      }
      transfer_summary: {
        Row: {
          amount: number | null
          date: string | null
          from_account: string | null
          from_description: string | null
          to_account: string | null
          to_description: string | null
          transaction_id: string | null
        }
        Relationships: []
      }
      yearly_summary: {
        Row: {
          account_name: string | null
          net: number | null
          total_received: number | null
          total_spent: number | null
          transaction_count: number | null
          year: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      calculate_holdings: {
        Args: { p_account_id: string; p_as_of_date: string }
        Returns: {
          cost_basis: number
          quantity: number
          symbol: string
        }[]
      }
      get_account_balance: {
        Args: { p_account_id: string; p_date: string }
        Returns: number
      }
      get_lifetime_spending: { Args: never; Returns: number }
      get_total_balance: { Args: { p_date: string }; Returns: number }
      refresh_all_summaries: { Args: never; Returns: undefined }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const

