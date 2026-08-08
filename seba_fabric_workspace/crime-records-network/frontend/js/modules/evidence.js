/**
 * Evidence chain: attach a commitment, list what is attached, read the private
 * detail. Only the hash is public; narrative detail goes to the
 * `evidenceDetails` private data collection (Police, Forensics, Court).
 */

import { api } from '../core/api.js';
import { FORENSIC_ROLES } from '../core/access.js';
import {
  card, grid, row, field, input, textarea, form, table, button, mono, hint,
  slot, replace, attempt, callout,
} from '../core/components.js';
import { dateTime, shortHash } from '../core/format.js';

function attachPanel() {
  const output = slot();

  const body = form({
    submitLabel: 'Attach evidence',
    fields: [
      row(
        field('Record ID', input('recordId', { placeholder: 'FIR-2026-0042', required: true })),
        field('Evidence ID', input('evidenceId', { placeholder: 'EV-DNA-001', required: true })),
      ),
      field('Artifact content', textarea('artifact', {
        required: true, rows: '2',
        placeholder: 'lab artifact bytes — only its SHA-256 goes on-chain',
      }), 'Hashed, never stored.'),
      field('Private detail', textarea('detail', {
        rows: '2', placeholder: 'goes to the evidenceDetails private collection',
      }), 'Visible to Police, Forensics and Court only.'),
    ],
    onSubmit: async (values, formNode) => {
      const result = await api.evidence.attach(values.recordId.trim(), {
        evidenceId: values.evidenceId.trim(),
        artifact: values.artifact,
        ...(values.detail ? { detail: values.detail } : {}),
      });
      replace(output, callout('good', 'Evidence commitment recorded',
        hint('Hash ', mono(shortHash(result.evidenceHash, 20)),
          ' · attached by ', result.attachedByRole)));
      formNode.reset();
    },
  });

  return card('Attach evidence',
    'The public ledger gets only the hash. Detail goes to a private data collection.',
    body, output);
}

function listPanel() {
  const output = slot();
  const detail = slot();

  const body = form({
    submitLabel: 'List evidence',
    fields: [field('Record ID', input('recordId', {
      placeholder: 'FIR-2026-0042', required: true,
    }))],
    onSubmit: async (values) => {
      const recordId = values.recordId.trim();
      const items = await api.evidence.list(recordId);
      replace(detail);
      replace(output, table(['Evidence', 'Hash', 'By', 'When', ''],
        items.map((item) => [
          mono(item.evidenceId),
          mono(item.evidenceHash, { truncate: true }),
          item.attachedByRole,
          dateTime(item.attachedAtUtc),
          button('Detail', {
            kind: 'ghost', small: true,
            onclick: async () => {
              const found = await attempt(() => api.evidence.detail(recordId, item.evidenceId));
              if (!found) return;
              replace(detail, callout('info', `Private detail for ${item.evidenceId}`,
                hint(found.detail)));
            },
          }),
        ]),
        { emptyMessage: 'No evidence attached to that record.' }));
    },
  });

  return card('Evidence chain', 'Commitments on a record, with private detail on demand.',
    body, output, detail);
}

export default {
  id: 'evidence',
  title: 'Evidence',
  group: 'Records',
  order: 40,
  // Anyone may list; only forensics may attach, so the attach panel is hidden
  // for others while the list stays available.
  allow: undefined,
  summary: 'Attach and inspect evidence commitments.',

  mount({ user }) {
    const canAttach = FORENSIC_ROLES.includes(user.role);
    return grid(canAttach ? attachPanel() : null, listPanel());
  },
};
