/**
 * Escalation queue — the review step of allow / deny / escalate.
 * Approving or rejecting is itself an on-chain transaction.
 */

import { api } from '../core/api.js';
import { APPROVER_ROLES } from '../core/access.js';
import {
  card, grid, table, button, mono, hint, subheading, slot, replace, append,
  asyncRegion, attempt, el,
} from '../core/components.js';
import { mspName, count } from '../core/format.js';
import { explanationCard, plainLanguageBlock } from '../shared/explanation.js';

export default {
  id: 'escalations',
  title: 'Escalation queue',
  group: 'Review',
  order: 10,
  allow: { roles: APPROVER_ROLES },
  summary: 'Requests the policy engine could not settle alone.',

  mount() {
    const detail = slot();

    const region = asyncRegion({
      load: () => api.access.pending(),
      render: (pending) => {
        if (pending.length === 0) return hint('No pending escalations.');

        const resolve = async (item, approve) => {
          const note = approve ? 'reviewed and approved' : 'rejected on review';
          const result = await attempt(
            () => (approve
              ? api.access.approve(item.recordId, item.decisionId, note)
              : api.access.reject(item.recordId, item.decisionId, note)),
            approve ? 'Escalation approved' : 'Escalation rejected');
          if (result) { replace(detail); region.reload(); }
        };

        const rows = pending.map((item) => [
          mono(item.recordId, { truncate: true }),
          `${item.subject.role} (${mspName(item.subject.mspId)})`,
          item.action,
          mono(item.explanation.reasonCode),
          el('div', { class: 'actions tight' },
            button('Why?', {
              kind: 'ghost', small: true,
              onclick: () => {
                replace(detail);
                append(detail, card(`Escalation detail — ${item.recordId}`, null,
                  explanationCard(item.explanation),
                  plainLanguageBlock(item.recordId, item.decisionId)));
              },
            }),
            button('Approve', { small: true, onclick: () => resolve(item, true) }),
            button('Reject', { kind: 'danger', small: true, onclick: () => resolve(item, false) })),
        ]);

        return el('div', {},
          hint(count(pending.length, 'request'), ' waiting for review.'),
          table(['Record', 'Requester', 'Action', 'Reason', 'Decide'], rows));
      },
    });

    return grid(
      card('Escalation queue',
        'Approving one is itself an on-chain event, attributed to your certificate.',
        el('div', { class: 'actions' },
          button('Refresh', { kind: 'ghost', onclick: () => region.reload() })),
        region),
      detail);
  },
};
