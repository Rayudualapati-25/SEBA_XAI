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
  card, row, field, input, select, form, table, button, badge, mono, hint,
  slot, replace, append, attempt, callout, asyncRegion,
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
    const results = slot({ 'aria-live': 'polite', 'aria-atomic': 'false' });
    const detail = slot({ 'aria-live': 'polite', 'aria-atomic': 'false' });
    const purpose = defaultPurpose(user.role);
    const caseInput = input('caseId', { placeholder: 'CASE-2026-001' });
    const caseButtons = new Map();

    const selectCase = (caseId) => {
      caseInput.value = caseId;
      for (const [id, node] of caseButtons) {
        node.classList.toggle('selected', id === caseId);
        node.setAttribute('aria-pressed', String(id === caseId));
      }
    };

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
      button('Request access', {
        small: true,
        ariaLabel: `Request access to ${record.recordId}`,
        onclick: () => requestAccess(record),
      }),
    ];

    const showResults = (found, caseId) => {
      replace(detail);
      if (found.length === 0) {
        replace(results, callout('info', `No files in ${caseId}`,
          hint('The case exists on Fabric, but no record metadata has been filed for it yet.')));
        return;
      }
      const sorted = [...found].sort((a, b) => a.recordId.localeCompare(b.recordId));
      replace(results,
        hint(count(sorted.length, 'record'), ' found. Metadata only — ',
          'opening a file requires an access decision.'),
        table(['Record', 'Case', 'Type', 'Sensitivity', 'Station', 'State', ''],
          sorted.map(resultRow)));
    };

    const searchByCase = async (caseId) => {
      selectCase(caseId);
      replace(results, hint(`Loading files for ${caseId}…`));
      const found = await attempt(() => api.records.search({ caseId }));
      if (found) showResults(found, caseId);
    };

    const caseRegion = asyncRegion({
      load: () => api.cases.list(),
      loadingMessage: 'Reading existing cases from Fabric…',
      render: (cases) => {
        caseButtons.clear();
        const sorted = [...cases].sort((a, b) => a.caseId.localeCompare(b.caseId));
        if (sorted.length === 0) {
          return callout('info', 'No cases on the ledger',
            hint('Create a case first, then return here to file or search its records.'));
        }

        return el('div', {},
          el('div', { class: 'case-browser-summary' },
            hint(count(sorted.length, 'case'), ' available on Fabric'),
            button('Refresh cases', { kind: 'ghost', small: true, onclick: () => caseRegion.reload() })),
          el('div', { class: 'case-picker', role: 'group', 'aria-label': 'Existing cases' },
            sorted.map((item) => {
              const option = el('button', {
                class: 'case-option', type: 'button',
                'aria-pressed': 'false',
                'aria-label': `View files for ${item.caseId}, ${item.status}, ${item.jurisdiction}`,
                onclick: () => searchByCase(item.caseId),
              },
              el('span', { class: 'case-option-top' },
                mono(item.caseId),
                badge(item.status, item.status === 'closed' ? 'neutral' : 'allow')),
              el('span', { class: 'case-option-meta' },
                item.jurisdiction || 'No jurisdiction'),
              el('span', { class: 'case-option-foot' },
                `${(item.assignedUsers || []).length} assigned · View files →`));
              caseButtons.set(item.caseId, option);
              return option;
            })));
      },
    });

    const body = form({
      submitLabel: 'Search case files',
      fields: [
        row(
          field('Case ID', caseInput),
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
        if (filters.caseId) selectCase(filters.caseId);
        showResults(found, filters.caseId || 'the selected filters');
      },
    });

    return el('div', { class: 'search-workspace' },
      card('Choose an existing case',
        'Demo shortcut: cases are read from GovernanceContract. Select one to load its files.',
        caseRegion),
      card('Search case files',
        'Refine by case, station, type or sensitivity. Search never grants content access.',
        body, results),
      detail);
  },
};
