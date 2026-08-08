/**
 * Full reconstruction of one record: every access decision with its explanation,
 * plus the record's own state history from the ledger.
 */

import { api } from '../core/api.js';
import { REVIEWER_ROLES } from '../core/access.js';
import {
  card, grid, field, input, form, table, button, badge, mono, hint, subheading,
  slot, replace, append, el,
} from '../core/components.js';
import { dateTime, shortHash, mspName } from '../core/format.js';
import {
  decisionBadge, explanationCard, plainLanguageBlock, verifyExplanationButton,
} from '../shared/explanation.js';

export default {
  id: 'audit-trail',
  title: 'Audit trail',
  group: 'Audit',
  order: 10,
  allow: { roles: REVIEWER_ROLES },
  summary: 'Every decision and explanation recorded for a record.',

  mount() {
    const output = slot();

    const body = form({
      submitLabel: 'Reconstruct trail',
      fields: [field('Record ID', input('recordId', {
        placeholder: 'FIR-2026-0042', required: true,
      }))],
      onSubmit: async (values) => {
        const recordId = values.recordId.trim();
        const trail = await api.audit.trail(recordId);
        const detail = slot();

        const decisions = [...trail.accessDecisions]
          .sort((a, b) => a.createdAtUtc.localeCompare(b.createdAtUtc));

        const decisionRows = decisions.map((d) => [
          dateTime(d.createdAtUtc),
          `${d.subject.role} (${mspName(d.subject.mspId)})`,
          d.action,
          decisionBadge(d.decision),
          badge(d.status, d.status.startsWith('approved') ? 'allow' : d.status),
          el('div', { class: 'actions tight' },
            button('Why?', {
              kind: 'ghost', small: true,
              onclick: () => {
                replace(detail);
                append(detail,
                  explanationCard(d.explanation),
                  plainLanguageBlock(recordId, d.decisionId));
              },
            }),
            verifyExplanationButton(recordId, d, detail)),
        ]);

        const historyRows = trail.recordHistory.map((h, index) => [
          String(index + 1),
          mono(shortHash(h.txId)),
          h.value
            ? (h.value.sealed ? badge('sealed', 'deny') : badge('open', 'allow'))
            : '—',
          h.value ? dateTime(h.value.sealChangedAtUtc || h.value.createdAtUtc) : '—',
        ]);

        replace(output,
          subheading('Access decisions'),
          table(['When', 'Requester', 'Action', 'Decision', 'Status', ''], decisionRows,
            { emptyMessage: 'No decisions recorded for this record.' }),
          detail,
          subheading('Record state history'),
          table(['#', 'Transaction', 'Seal state', 'When'], historyRows));
      },
    });

    return grid(card('Audit trail reconstruction',
      'Decisions, explanations and state history, straight from the ledger.',
      body, output));
  },
};
