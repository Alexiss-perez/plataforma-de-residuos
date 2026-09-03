// Tipos TypeScript generados desde Supabase
// Para el frontend: import { Database } from "./types/supabase"
// const supabase = createClient<Database>(URL, KEY)

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      ofertas_residuo: {
        Row: {
          created_at: string | null
          estado: string
          id: string
          material: string
          notas: string | null
          tipo_generador: string
          ubicacion: string
          usuario_id: string
          volumen: string
        }
        Insert: {
          created_at?: string | null
          estado?: string
          id?: string
          material: string
          notas?: string | null
          tipo_generador: string
          ubicacion: string
          usuario_id: string
          volumen: string
        }
        Update: {
          created_at?: string | null
          estado?: string
          id?: string
          material?: string
          notas?: string | null
          tipo_generador?: string
          ubicacion?: string
          usuario_id?: string
          volumen?: string
        }
        Relationships: [
          {
            foreignKeyName: "ofertas_residuo_usuario_id_fkey"
            columns: ["usuario_id"]
            isOneToOne: false
            referencedRelation: "usuarios"
            referencedColumns: ["id"]
          },
        ]
      }
      receptores: {
        Row: {
          capacidad_disponible: string | null
          created_at: string | null
          direccion: string
          id: number
          lat: number | null
          lon: number | null
          materiales_aceptados: string[]
          nombre: string
          telefono: string | null
          tipo: string
        }
        Insert: {
          capacidad_disponible?: string | null
          created_at?: string | null
          direccion: string
          id?: number
          lat?: number | null
          lon?: number | null
          materiales_aceptados?: string[]
          nombre: string
          telefono?: string | null
          tipo: string
        }
        Update: {
          capacidad_disponible?: string | null
          created_at?: string | null
          direccion?: string
          id?: number
          lat?: number | null
          lon?: number | null
          materiales_aceptados?: string[]
          nombre?: string
          telefono?: string | null
          tipo?: string
        }
        Relationships: []
      }
      retiros: {
        Row: {
          created_at: string | null
          estado: string
          fecha: string
          hora: string
          id: string
          oferta_id: string
          receptor_id: number
        }
        Insert: {
          created_at?: string | null
          estado?: string
          fecha: string
          hora: string
          id?: string
          oferta_id: string
          receptor_id: number
        }
        Update: {
          created_at?: string | null
          estado?: string
          fecha?: string
          hora?: string
          id?: string
          oferta_id?: string
          receptor_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "retiros_oferta_id_fkey"
            columns: ["oferta_id"]
            isOneToOne: false
            referencedRelation: "ofertas_residuo"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "retiros_receptor_id_fkey"
            columns: ["receptor_id"]
            isOneToOne: false
            referencedRelation: "receptores"
            referencedColumns: ["id"]
          },
        ]
      }
      usuarios: {
        Row: {
          created_at: string | null
          direccion: string | null
          email: string
          id: string
          nombre: string
          telefono: string | null
          tipo: string
        }
        Insert: {
          created_at?: string | null
          direccion?: string | null
          email: string
          id?: string
          nombre: string
          telefono?: string | null
          tipo: string
        }
        Update: {
          created_at?: string | null
          direccion?: string | null
          email?: string
          id?: string
          nombre?: string
          telefono?: string | null
          tipo?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      get_user_retiros: {
        Args: { p_user_id: string }
        Returns: {
          created_at: string
          destino: string
          estado: string
          fecha: string
          hora: string
          id: string
          material: string
          oferta_id: string
          origen: string
          receptor_id: number
          receptor_nombre: string
          volumen: string
        }[]
      }
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
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
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
