export type Option = {
  /** unique id used in state of select */
  id: string;
  /** display name */
  name?: string;
  /** count col */
  count?: number;
  /** tooltip on hover */
  tooltip?: string;
};

export type Options = Array<Option>;
