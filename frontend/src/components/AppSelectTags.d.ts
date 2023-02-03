/**
 * instead of providing a static list of options, you can provide this function
 * that receives the user-typed search string and dynamically returns a list of
 * options to display to user for selection or auto-select.
 */
export type OptionsFunc = (search: string) => Promise<{
  /** list of options to return */
  options: Options;
  /** whether to auto-select these options, or display to user for selection */
  autoAccept?: boolean;
  /** snackbar message to show when auto-accepting */
  message?: string;
}>;

export type Options = Array<Option>;

export type Option = {
  /** unique id used in state of select */
  id: string;
  /** icon name */
  icon?: string;
  /** display name */
  name?: string;
  /** highlighting html */
  highlight?: string;
  /** info col */
  info?: string;
  /** tooltip on hover */
  tooltip?: string;
  /**
   * allows returning multiple options instead when selecting this option, e.g.
   * clicking a gene result and getting/selecting its 8 associated phenotypes
   * instead
   */
  spreadOptions?: () => Promise<Options>;
};
