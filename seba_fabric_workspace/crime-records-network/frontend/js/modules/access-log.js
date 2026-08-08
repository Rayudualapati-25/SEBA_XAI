/**
 * The access log: who searched, who read a record, who received a case file.
 *
 * These are ledger *queries*, so they leave no transaction of their own. They are
 * recorded off-chain as a hash chain whose head is periodically committed to the
 * blockchain, which is what makes editing or deleting an entry detectable.
 */

import { api } from '../core/api.js';
import { REVIEWER_ROLES, OVERSIGHT_ROLES } from '../core/access.js';
import {
  card, grid, table, button, badge, hint, callout, slot, replace, append,
  asyncRegion, attempt, el,
} from '../core/components.js';
import { dateTime, actor, count } from '../core/format.js';
import { actionLabel, outcomeKind } from '../shared/vocab.js';

export default {
  id: 'access-log',
  title: 'Access log',
  group: 'Audit',
  order: 30,
  allow: { roles: REVIEWER_ROLES },
  summary: 'Searches and reads, with an integrity check against the ledger.',

  mount({ user }) {
    const verdict = slot();
    const mayAnchor = OVERSIGHT_ROLES.includes(user.role);

    const region = asyncRegion({
      load: () => api.audit.accessLog(60),
      render: (data) => el('div', {},
        hint(count(data.entries.length, 'entry', 'entries'),
          ' shown · anchored on-chain up to entry ', String(data.anchoredUpto),
          ' · ', String(data.pendingAnchor), ' waiting to be anchored'),
        table(['#', 'When', 'Who', 'Did what', 'Outcome'],
          data.entries.map((entry) => [
            String(entry.seq),
            dateTime(entry.ts),
            actor(entry.actor_username, entry.actor_role),
            actionLabel(entry.action),
            badge(entry.outcome, outcomeKind(entry.outcome)),
          ]),
          { emptyMessage: 'The log is empty.' })),
    });

    const verify = async () => {
      const result = await attempt(() => api.audit.verifyAccessLog());
      if (!result) return;
      replace(verdict, callout(result.ok ? 'good' : 'bad',
        'Log integrity',
        hint('Result: ', badge(result.ok ? 'intact' : 'tampered', result.ok ? 'allow' : 'deny')),
        hint(`${result.entriesChecked} entries re-hashed, `
          + `${result.anchorsChecked} on-chain anchor(s) compared.`),
        result.anchorError
          ? hint(`Warning: could not read anchors from the ledger (${result.anchorError}). `
            + 'Only the local chain was checked.')
          : null,
        result.priorEpochWarning ? hint(`Note: ${result.priorEpochWarning}`) : null,
        result.ok ? null : el('div', {},
          hint(`First bad entry: #${result.firstBadSeq}`),
          el('ul', { class: 'problem-list' },
            result.problems.slice(0, 6).map((p) => el('li', {}, p))))));
    };

    const anchorNow = async () => {
      const result = await attempt(() => api.audit.anchor());
      if (!result) return;
      replace(verdict, callout('info', 'Anchor',
        hint(result.anchored
          ? `Committed the log head up to entry ${result.anchor.seqNo} to the blockchain.`
          : `Nothing new to anchor (${result.reason}).`)));
      region.reload();
    };

    return grid(card('Access log (searches and reads)',
      'Reads and searches are ledger queries, so they leave no transaction. They are '
      + 'recorded here as a hash chain whose head is committed to the blockchain.',
      el('div', { class: 'actions' },
        button('Refresh', { kind: 'ghost', onclick: () => region.reload() }),
        button('Verify log integrity', { onclick: verify }),
        mayAnchor ? button('Anchor now', { kind: 'ghost', onclick: anchorNow }) : null),
      verdict, region));
  },
};
