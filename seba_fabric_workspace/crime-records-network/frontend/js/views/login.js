/**
 * Sign-in screen. Demo accounts are one-click chips so a reviewer can switch
 * departments quickly during a walkthrough.
 */

import { api } from '../core/api.js';
import { el } from '../core/dom.js';
import { card, field, input, button, hint } from '../core/components.js';
import { toast } from '../core/toast.js';

/** Kept in sync with the demo accounts seeded in backend/src/db.js. */
const DEMO_ACCOUNTS = Object.freeze([
  ['insp.sharma', 'Police · Inspector'],
  ['const.verma', 'Police · Constable'],
  ['sho.reddy', 'Police · SHO'],
  ['io.krishnan', 'Police · IO'],
  ['insp.rathore', 'Police · revoked credential'],
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
  const password = input('password', {
    type: 'password', value: 'demo123', autocomplete: 'current-password',
  });
  const submit = button('Sign in', { type: 'submit' });

  const form = el('form', {
    onsubmit: async (event) => {
      event.preventDefault();
      submit.disabled = true;
      try {
        onSignedIn(await api.auth.login(username.value.trim(), password.value));
      } catch (error) {
        toast(error.message, 'error');
      } finally {
        submit.disabled = false;
      }
    },
  },
  field('Username', username),
  field('Password', password),
  el('div', { class: 'actions' }, submit));

  const chips = DEMO_ACCOUNTS.map(([user, label]) =>
    el('button', {
      class: 'chip', type: 'button', title: user,
      onclick: () => { username.value = user; username.focus(); },
    }, label));

  return el('div', { class: 'login-wrap' },
    el('h1', {}, 'Crime Records Access Network'),
    hint('Permissioned Hyperledger Fabric network for inter-agency access governance. ',
      'Every action is signed with your own certificate and recorded on the ledger.'),
    card('Sign in', null, form,
      el('div', { class: 'demo-users' },
        el('h3', {}, 'Demo accounts · password demo123'),
        el('div', { class: 'chip-row' }, chips))));
}
