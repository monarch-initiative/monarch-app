import type { Instance } from "tippy.js";

/** When tippy instances attached to element */
const update = (instance: Instance): void => {
  if (
    /** Element has no text */
    !(instance.reference as HTMLElement).innerText?.trim() &&
    /** Element has no aria label already */
    !instance.reference.getAttribute("aria-label") &&
    /** Tooltip content is plain string */
    typeof instance.props.content === "string"
  )
    /** Set aria label from tooltip content as fallback */
    instance.reference.setAttribute("aria-label", instance.props.content);

  /**
   * If tooltip target/reference is plain text (not link, not button, etc), add
   * styling to indicate it has tooltip
   */
  if (instance.reference.tagName === "SPAN" && !!instance.props.content)
    instance.reference.setAttribute("data-tooltip", "true");
};

/** Cancel show if no content to show */
const onShow = (instance: Instance): boolean =>
  !!String(instance.props.content).trim();

/** Return false to inspect popup for debugging */
const onHide = (): boolean => true;

export const options = {
  directive: "tooltip",
  component: "tooltip",
  defaultProps: {
    delay: [300, 0],
    duration: 200,
    offset: [13, 13],
    allowHTML: true,
    onCreate: update,
    onAfterUpdate: update,
    onShow,
    onHide,
  },
};

/** https://github.com/KABBOUCHI/vue-tippy/issues/140 */
export const appendToBody = (): Element => document.body;
