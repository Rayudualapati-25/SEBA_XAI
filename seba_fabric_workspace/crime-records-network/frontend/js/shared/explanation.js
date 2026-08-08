/**
 * Rendering for the XAI explanation artifact.
 *
 * Shared by search, audit trail and the escalation queue — the same decision
 * must look the same everywhere, so this lives here rather than in one module.
 */

import { el, card, hint, mono, badge, callout, button, slot, replace, append }
  from '../core/components.js';
import { api } from '../core/api.js';
import { attributeList, dateTime, shortHash, mspName } from '../core/format.js';
import { REASON_TEXT, DECISION_CONSEQUENCE } from './vocab.js';

/** Coloured pill for allow / deny / escalate. */
export function decisionBadge(decision) {
  return badge(decision, decision);
}

/**
 * The structured artifact: what was decided, why, which attributes mattered,
 * and what would change the outcome. Always available — it comes from the
 * ledger and never depends on the AI.
 */
export function explanationCard(explanation) {
  if (!explanation) return null;
  return el('div', { class: 'explain' },
    el('div', { class: 'explain-why' },
      `Why ${explanation.decision}? `,
      REASON_TEXT[explanation.reasonCode] || explanation.reasonCode),
    el('dl', { class: 'explain-fields' },
      el('dt', {}, 'Reason code'), el('dd', {}, mono(explanation.reasonCode)),
      el('dt', {}, 'Decisive attributes'), el('dd', {}, attributeList(explanation.decisiveAttributes)),
      el('dt', {}, 'Counterfactual'), el('dd', {}, explanation.counterfactual || 'not applicable'),
      el('dt', {}, 'Policy version'), el('dd', {}, mono(explanation.policyVersion))));
}

/**
 * The AI's plain-language wording.
 *
 * The decision is NOT made here — it was already decided by the chaincode and
 * committed to the ledger. This asks the backend to reword that recorded
 * decision. If the model is unavailable or says something unsupported, the
 * backend returns deterministic template wording and labels it as such.
 */
export function plainLanguageBlock(recordId, decisionId) {
  const body = el('p', { class: 'plain-body loading' }, 'Generating…');
  const meta = slot({ class: 'plain-meta' });

  const container = el('div', { class: 'explain plain' },
    el('div', { class: 'explain-why' }, 'In plain language'),
    body, meta);

  api.explain.decision(recordId, decisionId)
    .then((result) => {
      body.textContent = result.text;
      body.classList.remove('loading');
      replace(meta);
      append(meta,
        result.source === 'llm'
          ? badge(`local LLM · ${result.model}`, 'allow')
          : badge('template wording', 'neutral'),
        result.cached ? badge('cached', 'neutral') : null,
        result.latencyMs ? el('small', {}, `${result.latencyMs} ms`) : null,
        result.problems?.length
          ? el('small', { class: 'block' }, `Model output rejected: ${result.problems.join('; ')}`)
          : null,
        result.warnings?.length
          ? el('small', { class: 'block' }, `Note: ${result.warnings.join('; ')}`)
          : null);
    })
    .catch((error) => {
      body.classList.remove('loading');
      body.textContent = 'Plain-language wording is unavailable. The structured '
        + 'explanation above is unaffected.';
      replace(meta, el('small', {}, error.message));
    });

  return container;
}

/**
 * Full decision view: header, structured artifact, AI wording, and what happens
 * next. Used wherever a single decision needs to be shown in detail.
 */
export function decisionDetail(decision, { extra } = {}) {
  return el('div', { class: 'decision-detail' },
    el('div', { class: 'decision-head' },
      el('strong', {}, 'Decision '), decisionBadge(decision.decision),
      hint('recorded on-chain as ', mono(shortHash(decision.decisionId, 20)),
        ' · ', dateTime(decision.createdAtUtc))),
    explanationCard(decision.explanation),
    plainLanguageBlock(decision.recordId, decision.decisionId),
    extra || hint(DECISION_CONSEQUENCE[decision.decision] || ''));
}

/** One decision as table cells: [when, who, action, decision, reason]. */
export function decisionRow(decision) {
  return [
    dateTime(decision.createdAtUtc),
    `${decision.subject.role} (${mspName(decision.subject.mspId)})`,
    decision.action,
    decisionBadge(decision.decision),
    mono(decision.explanation.reasonCode),
  ];
}

/**
 * "Verify this explanation" control: checks the artifact as recorded, then the
 * same artifact with a tampered reason code, so the difference is visible.
 */
export function verifyExplanationButton(recordId, decision, output) {
  return button('Verify', {
    kind: 'ghost', small: true,
    onclick: async () => {
      try {
        const genuine = await api.audit.verifyExplanation(
          recordId, decision.decisionId, decision.explanation);
        const forged = await api.audit.verifyExplanation(
          recordId, decision.decisionId,
          { ...decision.explanation, reasonCode: 'FORGED' });
        replace(output, callout('info', 'Explanation integrity check',
          hint('As recorded: ', badge(genuine.match ? 'match' : 'mismatch',
            genuine.match ? 'allow' : 'deny'),
          ' · on-chain hash ', mono(shortHash(genuine.storedHash))),
          hint('Same artifact with a tampered reason code: ',
            badge(forged.match ? 'match' : 'mismatch', forged.match ? 'allow' : 'deny'))));
      } catch (error) {
        replace(output, callout('bad', 'Verification failed', hint(error.message)));
      }
    },
  });
}

export { card };
