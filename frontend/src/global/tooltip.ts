import { Instance } from "tippy.js";

/** when tippy instances attached to element */
const update = (instance: Instance): void => {
  if (
    /** element has no text */
    !(instance.reference as HTMLElement).innerText?.trim() &&
    /** element has no aria label already */
    !instance.reference.getAttribute("aria-label") &&
    /** tooltip content is plain string */
    typeof instance.props.content === "string"
  )
    /** set aria label from tooltip content as fallback */
    instance.reference.setAttribute("aria-label", instance.props.content);

  /**
   * if tooltip target/reference is plain text (not link, not button, etc), add
   * styling to indicate it has tooltip
   */
  if (instance.reference.tagName === "SPAN" && !!instance.props.content)
    instance.reference.setAttribute("data-tooltip", "true");
};

/** cancel show if no content to show */
const onShow = (instance: Instance): boolean =>
  !!String(instance.props.content).trim();

/** return false to inspect popup for debugging */
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
