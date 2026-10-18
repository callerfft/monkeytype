import { isBuiltin } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const emptyMockHref = pathToFileURL(path.resolve('./scripts/empty-mock.js')).href;
const zodMockHref = pathToFileURL(path.resolve('./scripts/zod-mock.js')).href;

export async function resolve(specifier, context, nextResolve) {
  if (specifier === 'zod' || specifier === 'zod-urlsearchparams') {
    return nextResolve(zodMockHref, context);
  }
  if (
    specifier === 'animejs' ||
    specifier.startsWith('@monkeytype/schemas') ||
    specifier.startsWith('virtual:')
  ) {
    return nextResolve(emptyMockHref, context);
  }

  try {
    return await nextResolve(specifier, context);
  } catch (err) {
    if (err.code === 'ERR_MODULE_NOT_FOUND' && !isBuiltin(specifier)) {
      const parentURL = context.parentURL;
      if (parentURL && parentURL.startsWith('file://')) {
        const parentPath = fileURLToPath(parentURL);
        const parentDir = path.dirname(parentPath);
        const resolvedPath = path.resolve(parentDir, specifier);

        for (const ext of ['.ts', '.tsx', '.js', '/index.ts', '/index.js']) {
          const candidate = resolvedPath + ext;
          if (fs.existsSync(candidate)) {
            return nextResolve(pathToFileURL(candidate).href, context);
          }
        }
      }
    }
    throw err;
  }
}
