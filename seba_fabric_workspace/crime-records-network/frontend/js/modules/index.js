/**
 * THE MODULE REGISTRY.
 *
 * ============================================================================
 *  TO ADD A NEW MODULE
 *  1. create `js/modules/my-thing.js` exporting a default descriptor
 *  2. import it below and add it to MODULES
 *  That is all. Navigation, routing and access filtering happen automatically.
 * ============================================================================
 *
 * Descriptor shape:
 *
 *   export default {
 *     id:      'my-thing',        // URL becomes #/my-thing — must be unique
 *     title:   'My thing',        // shown in the sidebar
 *     group:   'Records',         // sidebar section: Records | Review | Audit | ...
 *     order:   50,                // sort order inside the group
 *     allow:   { roles: [...] },  // see core/access.js; omit for "everyone"
 *     summary: 'One line shown under the page title.',
 *     mount({ user, navigate }) { return someElement; },
 *   }
 *
 * `mount` is called every time the module is opened, so build fresh nodes and
 * kick off your own data loading (see `asyncRegion` in core/components.js).
 */

import fileRecord from './file-record.js';
import searchRecords from './search-records.js';
import recordLookup from './record-lookup.js';
import evidence from './evidence.js';
import escalations from './escalations.js';
import sealRecord from './seal-record.js';
import auditTrail from './audit-trail.js';
import payloadIntegrity from './payload-integrity.js';
import accessLog from './access-log.js';

export const MODULES = Object.freeze([
  fileRecord,
  searchRecords,
  recordLookup,
  evidence,
  escalations,
  sealRecord,
  auditTrail,
  payloadIntegrity,
  accessLog,
]);

/** Sidebar section order. Groups not listed here appear last, alphabetically. */
export const GROUP_ORDER = Object.freeze(['Records', 'Review', 'Audit']);

export function moduleById(id) {
  return MODULES.find((module) => module.id === id) || null;
}
