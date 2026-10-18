const chainable = () => new Proxy({}, {
  get: () => chainable,
  apply: () => chainable(),
});

export const z = new Proxy({}, {
  get: () => chainable,
});

export const literal = chainable;
export const string = chainable;
export const number = chainable;
export const boolean = chainable;
export const object = chainable;
export const array = chainable;
export const record = chainable;
export const tuple = chainable;
export const union = chainable;
export const intersection = chainable;
export const nativeEnum = chainable;
export const custom = chainable;
export const any = chainable;
export const unknown = chainable;
export const never = chainable;
export const coerce = chainable;

export class ZodObject {}
export class ZodTypeAny {}
export class ZodErrorMap {}
export class ZodString {}
export class ZodSchema {}
export class ZodType {}
export class ZodRecord {}
export class ZodArray {}
export class ZodUnion {}
export class ZodEnum {}
export class ZodLiteral {}
export class ZodNumber {}
export class ZodBoolean {}
export class ZodNativeEnum {}

export function safeParse() {
  return { success: false };
}
export function serialize() {
  return "";
}
