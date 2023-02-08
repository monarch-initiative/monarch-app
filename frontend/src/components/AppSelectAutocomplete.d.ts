export type OptionsFunc = (search: string) => Promise<Options>;

export type Options = Array<Option>;

export type Option = {
  /** icon name */
  icon?: string;
  /** display name */
  name: string;
  /** highlighting html */
  highlight?: string;
  /** info col */
  info?: string;
  /** tooltip on hover */
  tooltip?: string;
};
