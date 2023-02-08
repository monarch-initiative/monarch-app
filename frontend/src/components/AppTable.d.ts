/** table column */
export interface Col {
  /**
   * unique id, used to identify/match for sorting, filtering, and named slots.
   * use "divider" to create vertical divider to separate cols
   */
  id: string;
  /** what item in row object to access as raw cell value */
  key?: string;
  /** header display text */
  heading?: string;
  /** how to align column contents (both header and body) horizontally */
  align?: "left" | "center" | "end";
  /**
   * width to apply to heading cell, in any valid css grid col width (px, fr,
   * auto, minmax, etc)
   */
  width?: string;
  /** whether to allow sorting of column */
  sortable?: boolean;
}

/** object with arbitrary keys */
// eslint-disable-next-line
export type Row = Record<string | number, any>;

/** arrays of rows and cols */
export type Cols = Array<Col>;
export type Rows = Array<Row>;

/** sort prop */
export type Sort = {
  id: string;
  direction: "up" | "down";
} | null;
