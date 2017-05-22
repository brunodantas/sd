
/**
 * Structs can also be exceptions, if they are nasty.
 */
exception NotFound {
  1: string dsc
}


service Graph {
  void ping(),

  string add_upd_vertex(1:i32 nome, 2:i32 cor, 3:string desc, 4:double peso),

  string add_upd_edge(1:i32 v1, 2:i32 v2, 3:double peso, 4:bool bi_flag) throws (1:NotFound ex),

  string get_vertex(1:i32 nome) throws (1:NotFound ex),

  string get_edge(1:i32 v1, 2:i32 v2) throws (1:NotFound ex),

  string del_vertex(1:i32 nome) throws (1:NotFound ex),

  string del_edge(1:i32 v1, 2:i32 v2) throws (1:NotFound ex),

  string list_edges(1:i32 nome) throws (1:NotFound ex),

  string list_vertices(1:i32 v1, 2:i32 v2) throws (1:NotFound ex),

  string list_neighbors(1:i32 nome) throws (1:NotFound ex)
}
