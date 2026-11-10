# OpenAI Archive Import

The OpenAI archive adapter preserves native message text, identities and graph relationships.

The adapter uses mapping-node parent links to recover all branches, independently of JSON object key order or `current_node`. Original epoch timestamps are interpreted as UTC Unix seconds. Topological traversal uses native timestamps to order ready branches, with stable ID ties; sibling ordering does not assert a response relationship. The exact native parent is indexed, including excluded reasoning ancestors; normalized parent anchors resolve through excluded ancestors to the nearest retained communication. Distinct `metadata.parent_id` relationships remain in the original and are not silently substituted for mapping edges.

Native `text` and `multimodal_text` string parts retain their original text and order without significance filtering, trimming, citation rewriting or acknowledgment requirements. Typed `thoughts` and `reasoning_recap`, explicit hidden channels, system/developer and tool-directed events remain native-only. Unknown content types are disclosed. Attachment-only user communications retain identities and source pointers without fabricated text or recovered attachment claims.

Group-chat messages use original timestamps for chronology while preserving native source indices. Roles, identities and completeness must reflect the actual supplied source.

Every new transcript remains unreviewed. Native completeness, attachment inventory reconciliation, retrieval, topic indexing and downstream intellectual processing remain pending. Raw-source credential holds, transcript credential holds and the ZIP storage limit are separate issues; none are bypassed by normalization or a successful mechanical verification.

Verification independently reopens native JSON, resolves exact field spans, enumerates all eligible messages across all graph branches, checks original roles, IDs, timestamps and ancestry, and rejects omitted alternatives or partial text. Synthetic tests cover unordered and branched graphs, cycles and missing parents, literal user text, reasoning exclusion, unknown times, attachment-only messages, exact source spans and group chronology. Use the separate user-review and capture-scope procedures for meaning and source completeness.
