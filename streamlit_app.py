import streamlit as st

st.set_page_config(
    page_title="Cognitai Client FAQ",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container { max-width: 860px; padding-top: 2.5rem; }
        .faq-hero {
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            color: #ffffff;
            padding: 2.2rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.75rem;
        }
        .faq-hero h1 { color: #ffffff; margin: 0 0 .4rem 0; font-size: 2rem; }
        .faq-hero p { color: #dbe4f0; margin: 0; font-size: 1.02rem; line-height: 1.5; }
        .faq-note {
            background: #f1f5f9;
            border-left: 4px solid #2c5282;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            font-size: .93rem;
            color: #334155;
            margin-bottom: 1.5rem;
        }
        div[data-testid="stExpander"] details {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            margin-bottom: .55rem;
        }
        div[data-testid="stExpander"] summary { font-weight: 600; font-size: 1.02rem; }
        .contact-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            margin-top: 1rem;
            line-height: 1.6;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="faq-hero">
        <h1>🧠 Cognitai Client FAQ</h1>
        <p>Session Transcription, Clinical Intelligence, and Documentation Support</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="faq-note">
        This FAQ provides additional information about how Cognitai may be used by your
        mental health professional. It supplements the Cognitai Informed Consent form and
        applicable privacy notices.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# FAQ content
# ---------------------------------------------------------------------------
FAQS = [
    (
        "1. What is Cognitai?",
        """
Cognitai is a clinical intelligence platform that supports you and your clinician
throughout your care. It brings together information from your therapy sessions and
anything you choose to share between sessions such as check-ins, journals, assigned
activities, and optional sleep or activity data to help your clinician better understand
your experiences over time. By organizing this information into clear, traceable insights
and supporting session preparation and documentation, Cognitai helps your clinician to be
even more present with you during sessions, spend less time rebuilding context or taking
notes, and focus more fully on what matters to you. Your clinician remains fully
responsible for every clinical decision, and Cognitai is designed to strengthen — not
replace — the relationship between you and your clinician.

Cognitai does not provide therapy, diagnose conditions, prescribe treatment, give
independent medical advice, or make clinical decisions. Your clinician remains responsible
for your care.
""",
    ),
    (
        "2. Why might my clinician use Cognitai?",
        """
Your clinician may use Cognitai to:

- Remain even more present during your session.
- Prepare draft clinical documentation.
- Organize relevant information discussed during sessions.
- Identify patterns, changes, themes, and possible associations for clinical review.
- Maintain continuity across sessions.
- Support more precise and personalized care.

Cognitai supports your clinician's professional judgment rather than replacing it.
""",
    ),
    (
        "3. Does Cognitai automatically record my sessions?",
        """
**No. Session transcription does not begin automatically.**

Your clinician must intentionally start transcription. The clinician dashboard displays a
clear indicator while transcription is active.

Your clinician can pause or stop transcription at any time, including during particularly
sensitive parts of a session.
""",
    ),
    (
        "4. What happens to the session audio?",
        """
Session audio is processed only for the purpose of producing the transcript.

The audio is **not retained** as part of your clinical records. It is deleted from the
transcription-processing infrastructure immediately after transcription is completed.

The written transcript may remain available within Cognitai, subject to your clinician's
decisions and applicable retention requirements.
""",
    ),
    (
        "5. Where is the transcript stored?",
        """
The transcript is stored only within Cognitai's secure infrastructure located in
**Quebec, Canada**.

Identifiable client information stored by Cognitai is encrypted. Cognitai also applies
additional layers of encryption to client content beyond the encryption provided by its
underlying infrastructure.
""",
    ),
    (
        "6. Is Cognitai a clinical record system?",
        """
No. Cognitai is a clinical intelligence platform rather than the clinician's official
electronic health record or medical-record system.

Your clinician may copy or export relevant insights or notes from Cognitai into the
clinic's official record system. Once information has been copied into another system, that
copy is governed by the clinic's record-retention, privacy, and legal obligations.
""",
    ),
    (
        "7. Can the transcript be deleted?",
        """
Yes. Your clinician may keep or delete the transcript after the analysis and documentation
have been completed, subject to applicable legal, regulatory, professional, and
clinical-record requirements.

You may also request deletion through your clinician.

Deletion may not apply to information that:

- Has already been copied into the clinic's official record.
- Must be retained under applicable healthcare or professional-record requirements.
- Must be retained to satisfy a legal obligation.
""",
    ),
    (
        "8. Where is identifiable client information stored?",
        """
Identifiable personal and health-related information held by Cognitai is encrypted and
stored in **Quebec, Canada**.

Cognitai does not send directly identifiable client information to external processors or
technology providers.
""",
    ),
    (
        "9. Can information be processed outside Canada?",
        """
Information that has first been de-identified may be processed inside or outside Canada to
provide specific technical services.

Before external processing, identifying information is removed or separated so that the
external technology provider does not receive directly identifiable client information.

External providers must be subject to appropriate privacy, security, confidentiality, and
data-processing obligations. Where HIPAA applies, this includes a Business Associate
Agreement when required.

External providers are prohibited from using any information for their own purposes or for
any model training.
""",
    ),
    (
        "10. Who can access my information?",
        """
Readable client information is limited to:

- Your treating clinician.
- Clinically authorized supervisors or other authorized clinical personnel where required
  for your care, supervision, or professional practice.

Access is based on clinical role and authorization.

**Cognitai employees and contractors do NOT have any readable access** to session
transcripts, clinical content, or identifying client information.
""",
    ),
    (
        "11. Can Cognitai staff read my transcript?",
        """
Cognitai personnel do **NOT** have any access to readable client content.

Client content is encrypted, including through an additional Cognitai encryption layer.
Cognitai's systems are designed so that staff cannot browse, search, or read client
sessions.

Any exceptional access mechanism required for security, legal compliance, or technical
recovery must be strictly controlled, authorized, and logged in accordance with Cognitai's
security procedures.
""",
    ),
    (
        "12. Does Cognitai use other technology providers?",
        """
Cognitai may use carefully selected technology providers for limited functions such as
infrastructure, secure processing, system reliability, and transcription.

These providers must:

- Process information only according to Cognitai's instructions.
- Use the information only to provide the contracted service.
- Maintain confidentiality and appropriate security safeguards.
- Refrain from selling the information.
- Refrain from using the information for advertising.
- Refrain from using it to train or improve their own AI models.
- Delete transient processing data according to Cognitai's instructions.
- Enter into appropriate contractual privacy and security agreements, including a BAA where
  HIPAA requires one.
""",
    ),
    (
        "13. Does Cognitai sell client data?",
        """
**No — and NEVER.** Cognitai does NOT sell personal, clinical, or health-related
information.
""",
    ),
    (
        "14. Is my information used to train AI models or improve Cognitai?",
        """
**NOT without your separate, explicit, and voluntary consent.**

Consent to session transcription and clinical documentation does not constitute consent to:

- AI-model training.
- Product-development research using your client content.
- Human review for model improvement.
- Participation in a research study.

Any use of client information for research, training, or product-improvement purposes
requiring client data would require a separate consent and voluntary enrolment process.

Declining such participation will not affect access to care.
""",
    ),
    (
        "15. Does Cognitai do more than create a transcript?",
        """
Yes. Transcription is only one small part of Cognitai. By integrating Cognitai into your
care, it can help:

- Give your clinician a clearer understanding of what happens between sessions
- Bring together your check-ins, journals, assigned activities, session information, and
  optional sleep or activity data
- Highlight meaningful changes and patterns over time
- Help your clinician prepare for each session with better context
- Reduce the time spent rebuilding context, taking notes, and completing documentation
- Help your clinician be even more present and focused during your sessions
- Support more personalized resources and follow-up between sessions
- Strengthen continuity throughout your care

Cognitai supports your clinician's professional judgment without replacing it. Your
clinician remains fully responsible for every clinical decision.
""",
    ),
    (
        "16. How can I know why Cognitai surfaced an insight?",
        """
Cognitai is designed carefully and responsibly to make its clinical-support outputs
traceable.

Analytical statements should be connected to supporting information, which may include:

- Relevant parts of the session.
- Information you provided between sessions.
- Your clinician's observations or notes.
- Previous clinical context available to the clinician.
- Other authorized information relevant to your care.

Your clinician reviews the supporting information and decides whether an output is
clinically meaningful.
""",
    ),
    (
        "17. Does Cognitai independently diagnose me or determine my treatment?",
        """
**NO.**

Cognitai does not:

- Diagnose mental health conditions.
- Make automated treatment decisions.
- Prescribe or change treatment.
- Replace your clinician.
- Independently determine what becomes part of your care plan.

Cognitai may surface information for your clinician to consider. Your clinician remains
responsible for evaluating that information and making all clinical decisions.
""",
    ),
    (
        "18. Are Cognitai's outputs reviewed by my clinician?",
        """
Yes. Your clinician is responsible for reviewing Cognitai-generated transcripts,
documentation, summaries, insights, and other outputs before relying on them in your care.

An AI-generated output should not replace your clinician's professional judgment.
""",
    ),
    (
        "19. Will Cognitai automatically add information to my official clinical record?",
        """
No. Cognitai is not the clinic's official record system.

Your clinician decides what information, if any, should be copied into the official
clinical record. The clinician remains responsible for reviewing and approving that
information.
""",
    ),
    (
        "20. Can my clinician share a session summary with me?",
        """
Yes. Cognitai may help prepare a client-friendly summary.

Your clinician decides whether sharing a summary is clinically appropriate, what it should
contain, and when it should be provided.
""",
    ),
    (
        "21. Does the transcription identify me by my voice?",
        """
Cognitai does not use voice recognition to determine your identity.

For purposes of organizing the transcript, the system may distinguish between the person
acting as the clinician and the person acting as the client. This is **speaker-role
labeling, not biometric identity recognition.**
""",
    ),
    (
        "22. Can I withdraw my consent?",
        """
Yes. You may withdraw consent for Cognitai to be used in future sessions at any time by
informing your clinician.

Requesting access, correction, or deletion of information is subject to applicable laws and
professional-record obligations.

Withdrawal of consent does not necessarily require deletion of information that:

- Was processed before consent was withdrawn.
- Has become part of the clinic's official clinical record.
- Must be retained under applicable law or professional standards.

Your clinician can explain how future sessions will be documented after consent is
withdrawn.
""",
    ),
    (
        "23. Who should I contact to access or delete my information?",
        """
You may make a request through:

- Your treating clinician or clinic.
- Cognitai's Privacy Office through your Cognitai Mobile App.

When a request directly affects the clinical relationship or clinical record, Cognitai may
inform or coordinate with your clinician.

Requests will be handled in accordance with applicable privacy, healthcare, professional,
and record-retention requirements.
""",
    ),
    (
        "24. How long is information retained?",
        """
Cognitai retains information only for as long as necessary to provide your clinician with
clinical intelligence services and meet applicable legal, regulatory, contractual, and
professional obligations.

Because Cognitai is not the official clinical-record system, retention may also depend on
decisions made by your clinician and the requirements that apply to the clinician's
practice.

Your clinician may delete a transcript after the relevant analysis and documentation have
been completed, unless retention is otherwise required.
""",
    ),
    (
        "25. What happens if I do not consent to Cognitai?",
        """
Using Cognitai is a mutual decision between you and your clinician.

You will continue to receive care if you do not consent to Cognitai. Your clinician will
use an alternative process to take notes and prepare clinical documentation.

Cognitai is intended to help provide greater continuity, precision, and personalization,
but it is not a condition for receiving mental healthcare.
""",
    ),
    (
        "26. Is Cognitai available for minors?",
        """
Cognitai is currently intended primarily for adults.

Any use involving a minor must follow the consent, authorization, parental or guardian
involvement, privacy, and professional requirements applicable in the relevant
jurisdiction.

The clinician or clinic is responsible for confirming that the necessary authorization has
been obtained before using Cognitai with a minor.
""",
    ),
    (
        "27. Is Cognitai an emergency or crisis-monitoring service?",
        """
**NO. Cognitai is NOT an emergency service** and does not continuously monitor sessions or
client information for immediate crises.

Do **NOT** use Cognitai to request urgent help. In an emergency, contact emergency services
or follow the emergency and crisis instructions provided by your clinician.
""",
    ),
    (
        "28. What happens if there is a privacy or security incident?",
        """
Cognitai maintains procedures to investigate and respond to suspected privacy or security
incidents.

Affected individuals, clinics, regulators, or other parties will be notified where
notification is required by applicable law and according to our privacy policy.
""",
    ),
]

# ---------------------------------------------------------------------------
# Search + render
# ---------------------------------------------------------------------------
query = st.text_input(
    "Search the FAQ",
    placeholder="Search by keyword (e.g. audio, consent, storage, minors)...",
    label_visibility="collapsed",
)

if query:
    q = query.lower()
    matches = [(t, b) for t, b in FAQS if q in t.lower() or q in b.lower()]
    if matches:
        st.caption(f"Showing {len(matches)} result(s) for “{query}”.")
    else:
        st.warning(f"No results found for “{query}”. Try a different keyword.")
else:
    matches = FAQS

for title, body in matches:
    with st.expander(title, expanded=bool(query)):
        st.markdown(body)

# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
st.divider()
st.subheader("29. Who can answer additional questions?")
st.write(
    "You may ask your clinician questions before signing the consent form or at any point "
    "during your care."
)
st.markdown(
    """
    <div class="contact-card">
        Questions concerning Cognitai's privacy and data practices may be directed to:<br><br>
        <strong>Privacy Officer</strong><br>
        Cognitai Health Inc.<br>
        1250 Rue Guy, Suite 600<br>
        Montréal, Quebec H3H 2L3<br>
        Email: <a href="mailto:trust@cognitai.org">trust@cognitai.org</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "This FAQ supplements the Cognitai Informed Consent form and applicable privacy "
    "notices. It does not replace clinical advice from your treating clinician."
)
