/** euclidean distance between two points */
export const dist = (x1 = 0, y1 = 0, x2 = 0, y2 = 0): number =>
  Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

/** trig funcs in degrees */
export const sin = (degrees = 0): number =>
  Math.sin((2 * Math.PI * degrees) / 360);
export const cos = (degrees = 0): number =>
  Math.cos((2 * Math.PI * degrees) / 360);

/** wrap number between range */
export const wrap = (value: number, min: number, max: number): number => {
  if (value > max) return min;
  if (value < min) return max;
  return value;
};

/** STUFF ONLY USED FOR HEADER VISUALIZATION */

/** point tuple types */
export interface Point3d {
  x: number;
  y: number;
  z: number;
}
export interface Point2d {
  x: number;
  y: number;
}

/** rotate a point in 3d about the x axis */
export const rotateX = ({ x, y, z }: Point3d, angle = 0): Point3d => ({
  x,
  y: y * cos(angle) - z * sin(angle),
  z: y * sin(angle) + z * cos(angle),
});

/** rotate a point in 3d about the y axis */
export const rotateY = ({ x, y, z }: Point3d, angle = 0): Point3d => ({
  x: x * cos(angle) + z * sin(angle),
  y,
  z: z * cos(angle) - x * sin(angle),
});

/** translate a point */
export const translate = (
  point: Point3d,
  offset: Point3d,
  scale = 1
): Point3d => ({
  x: point.x + offset.x * scale,
  y: point.y + offset.y * scale,
  z: point.z + offset.z * scale,
});

/** rotate a point in 3d about x and y axis around an offset point */
export const project = (
  point: Point3d,
  xAngle = 0,
  yAngle = 0,
  offsetX = 0,
  offsetY = 0
): Point2d => {
  const offset = { x: offsetX, y: offsetY, z: 0 };
  point = translate(point, offset, -1);
  point = rotateX(point, xAngle);
  point = rotateY(point, yAngle);
  point = translate(point, offset);
  const { x, y } = point;
  return { x, y };
};

/** get midpoint of line segment */
export const getMidpoint = (a: Point3d, b: Point3d): Point3d => ({
  x: (a.x + b.x) / 2,
  y: (a.y + b.y) / 2,
  z: (a.z + b.z) / 2,
});
