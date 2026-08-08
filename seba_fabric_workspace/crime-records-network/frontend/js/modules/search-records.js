/**
 * Search case files, then request access to a result.
 *
 * Searching returns metadata only and grants nothing. Requesting access runs the
 * on-chain policy engine and shows the explanation inline — this is where the
 * access-control, blockchain and explainable-AI layers are all visible at once.
 */

import { api } from '../core/api.js';
import { el } from '../core/dom.js';
import {
  card, grid, row, field, input, select, form, table, button, badge, mono, hint,
  slot, replace, append, attempt,
} from '../core/components.js';
import { RECORD_TYPES, SENSITIVITY, defaultPurpose } from '../shared/vocab.js';
import { decisionDetail } from '../shared/explanation.js';
import { count } from '../core/format.js';

const ANY = '— any —';

export default {
  id: 'search',
  title: 'Search case files',
  group: 'Records',
  order: 20,
  allow: undefined, // every signed-in user may search; the ledger gates content
  summary: 'Find records by case, station, type or sensitivity.',

  mount({ user }) {
    const results = slot();
    const detail = slot();
    const purpose = defaultPurpose(user.role);

    /** Ask for access to one result and render the decision below the table. */
    const requestAccess = async (record) => {
      const decision = await attempt(() => api.access.request({
        recordId: record.recordId, action: 'view', purpose,
      }));
      if (!decision) return;

      const opened = slot();
      const openButton = decision.decision === 'allow'
        ? button('Open case file', {
          small: true,
          onclick: async () => {
            const released = await attempt(() => api.records.payload(record.recordId));
            if (!released) return;
            replace(opened, el('pre', { class: 'mono block' },
              JSON.stringify(released.payload, null, 2)));
          },
        })
        : null;

      replace(detail);
      append(detail, card(`Access decision for ${record.recordId}`, null,
        decisionDetail({ ...decision, recordId: record.recordId }),
        openButton, opened));
      detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };

    const resultRow = (record) => [
      mono(record.recordId),
      mono(record.caseId),
      record.recordType,
      badge(record.sensitivityLevel, 'neutral'),
      record.owningStation,
      record.sealed ? badge('sealed', 'deny') : badge('open', 'allow'),
      button('Request access', { small: true, onclick: () => requestAccess(record) }),
    ];

    const body = form({
      submitLabel: 'Search case files',
      fields: [
        row(
          field('Case ID', input('caseId', { placeholder: 'CASE-2026-001' })),
          field('Station', input('owningStation', { placeholder: 'PS-Central' })),
        ),
        row(
          field('Record type', select('recordType', [ANY, ...RECORD_TYPES])),
          field('Sensitivity', select('sensitivityLevel', [ANY, ...SENSITIVITY])),
        ),
      ],
      onSubmit: async (values) => {
        const filters = {};
        if (values.caseId.trim()) filters.caseId = values.caseId.trim();
        if (values.owningStation.trim()) filters.owningStation = values.owningStation.trim();
        if (values.recordType !== ANY) filters.recordType = values.recordType;
        if (values.sensitivityLevel !== ANY) filters.sensitivityLevel = values.sensitivityLevel;

        if (Object.keys(filters).length === 0) {
          throw new Error('Enter a case ID or pick at least one filter.');
        }

        const found = await api.records.search(filters);
        replace(detail);
        if (found.length === 0) {
          replace(results, hint('No records match those filters.'));
          return;
        }
        const sorted = [...found].sort((a, b) => a.recordId.localeCompare(b.recordId));
        replace(results,
          hint(count(sorted.length, 'record'), ' found. Metadata only — ',
            'opening a file requires an access decision.'),
          table(['Record', 'Case', 'Type', 'Sensitivity', 'Station', 'State', ''],
            sorted.map(resultRow)));
      },
    });

    return grid(
      card('Search case files',
        'Searching reveals no contents. Requesting access runs the on-chain policy engine.',
        body, results),
      detail);
  },
};
