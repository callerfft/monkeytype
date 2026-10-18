import fs from 'fs';
import path from 'path';

console.log("=== Node.js Contract Verification: Worker M1-2 ===");

const contractPath = path.resolve('contracts/api_v1.json');
const raw = fs.readFileSync(contractPath, 'utf8');
const doc = JSON.parse(raw);

let passed = 0;
let failed = 0;

function check(name, condition, msg = "") {
  if (condition) {
    passed++;
    console.log(`[PASS] ${name}`);
  } else {
    failed++;
    console.error(`[FAIL] ${name}: ${msg}`);
  }
}

// 1. Syntax & Document Structure
check("Valid JSON syntax and root keys", doc.openapi === "3.1.0" && doc.components && doc.components.schemas);
const schemas = doc.components.schemas;
check("23 schemas declared in components", Object.keys(schemas).length === 23);

// 2. Reference Resolution
const dollarRef = "$" + "ref";
const refs = [];
function findRefs(obj) {
  if (!obj || typeof obj !== 'object') return;
  for (const k of Object.keys(obj)) {
    if (k === dollarRef) refs.push(obj[k]);
    else findRefs(obj[k]);
  }
}
findRefs(doc);
const brokenRefs = refs.filter(r => {
  const name = r.replace('#/components/schemas/', '');
  return !schemas[name];
});
check(`All ${refs.length} references resolve (0 broken)`, brokenRefs.length === 0, `Broken: ${brokenRefs.join(', ')}`);

// 3. Fix 1: SSETokenPayload
const tokenPayload = schemas.SSETokenPayload;
check("SSETokenPayload requires 'text'", Array.isArray(tokenPayload.required) && tokenPayload.required.includes("text"));
check("SSETokenPayload has additionalProperties: false", tokenPayload.additionalProperties === false);

// 4. Fix 2: SSEStreamEvent.properties.data
const streamEvent = schemas.SSEStreamEvent;
const dataProp = streamEvent.properties.data;
check("SSEStreamEvent.properties.data uses anyOf", Array.isArray(dataProp.anyOf));
check("SSEStreamEvent.properties.data removed oneOf", dataProp.oneOf === undefined);

const inlineErrorBranch = dataProp.anyOf.find(b => b.type === "object" && b.properties && b.properties.errors);
check("SSEStreamEvent data has inline error branch", !!inlineErrorBranch);
if (inlineErrorBranch) {
  check("Inline error branch requires 'errors'", Array.isArray(inlineErrorBranch.required) && inlineErrorBranch.required.includes("errors"));
  check("Inline error branch has additionalProperties: false", inlineErrorBranch.additionalProperties === false);
}

// 5. Fix 3: SessionMetrics.required contains target_met
const sessionMetrics = schemas.SessionMetrics;
check("SessionMetrics requires target_met", Array.isArray(sessionMetrics.required) && sessionMetrics.required.includes("target_met"));

// 6. Fix 4: EvaluationRequest.properties.user_text minLength is 0
const evalRequest = schemas.EvaluationRequest;
check("EvaluationRequest.user_text minLength is 0", evalRequest.properties.user_text.minLength === 0);

console.log(`\nTotal checks: ${passed + failed}`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);

if (failed > 0) {
  process.exit(1);
} else {
  console.log("\nALL NODE CHECKS PASSED (100% SUCCESS)");
}
