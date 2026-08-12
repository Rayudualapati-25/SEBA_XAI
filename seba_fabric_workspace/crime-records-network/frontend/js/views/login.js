/**
 * Local Fabric-identity selector. Demo accounts are one-click chips so a
 * reviewer can switch departments quickly during a walkthrough.
 */

import { api } from '../core/api.js';
import { el } from '../core/dom.js';
import { card, field, input, button, hint } from '../core/components.js';
import { toast } from '../core/toast.js';

/**
 * Kept in sync with the roster in scripts/seed-users-onchain.js, which is what
 * writes these profiles onto the ledger. If sign-in cannot verify any of them,
 * their Fabric identities or ledger profiles are missing — run
 * `make seed-users`.
 */
const DEMO_ACCOUNTS = Object.freeze([
  ['insp.sharma', 'Police · Inspector'],
  ['const.verma', 'Police · Constable'],
  ['sho.reddy', 'Police · SHO'],
  ['io.krishnan', 'Police · IO'],
  ['insp.rathore', 'Police · revoked credential'],
  ['insp.singh', 'Police · cross-district request'],
  ['analyst.rao', 'Forensics · Analyst'],
  ['dir.iyer', 'Forensics · Director'],
  ['pp.mehta', 'Prosecution · Public Prosecutor'],
  ['dc.nair', 'Prosecution · Defense Counsel'],
  ['judge.rana', 'Court · Judge'],
  ['clerk.das', 'Court · Clerk'],
  ['aud.qureshi', 'Audit · Auditor'],
  ['omb.pillai', 'Audit · Ombudsman'],
]);

export function loginView(onSignedIn) {
  const username = input('username', { placeholder: 'insp.sharma', autocomplete: 'username' });
  const submit = button('Use Fabric identity', { type: 'submit' });

  const form = el('form', {
    onsubmit: async (event) => {
      event.preventDefault();
      submit.disabled = true;
      try {
        onSignedIn(await api.auth.login(username.value.trim()));
      } catch (error) {
        toast(error.message, 'error');
      } finally {
        submit.disabled = false;
      }
    },
  },
  field('Enrolled identity', username,
    'The local backend signs a Fabric identity check with this certificate.'),
  el('div', { class: 'actions' }, submit));

  const chips = DEMO_ACCOUNTS.map(([user, label]) =>
    el('button', {
      class: 'chip', type: 'button', title: user,
      onclick: () => { username.value = user; username.focus(); },
    }, label));

  return el('div', { class: 'login-wrap' },
    el('h1', {}, 'Crime Records Access Network'),
    hint('Permissioned Hyperledger Fabric network for inter-agency access governance. ',
      'No application password database is used.'),
    card('Select a local Fabric identity',
      'Development mode: certificates and private keys are held by this local backend. '
      + 'Production users should prove possession of a client-held key.', form,
      el('div', { class: 'demo-users' },
        el('h3', {}, 'Enrolled demo identities'),
        el('div', { class: 'chip-row' }, chips))));
}
