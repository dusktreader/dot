Sorry I took a bit to respond, but I wanted to make sure my response was well researched first.

First, the DMS tasks are still required. Both acn-assess-recap-qalv-dms-repl-inst-task and
acn-assess-recap-qastg-dms-repl-inst-task feed RECAP via Kinesis. Please do not delete them. The tasks are healthy and
active in the DMS console.

Second, the inactive ~117 GB slot seems abandoned. It is most likely a leftover from an old rollout of RECAP during our
testing phase. It can be safely dropped to reclaim the space. I queried pg_replication_slots on the cluster and found
three slots, all using test_decoding:

Slot         Database         Active
jnl6eodv...  authoring_qastg  true
y6pgf6ph...  authoring_qalv   true
vfpmcxw6...  authoring_qastg  false

Evidence it is abandoned:
- There are two QASTG slots but only one QASTG DMS task. The active one (jnl6eodv...) is the one in use.
- The inactive slot has no backend PID, no usename and no client_addr. Nothing has connected to it.
- Its restart_lsn is 0/BE164478, while the active slots are at 1E/1A.... It is roughly 30 GB of LSN positions behind in
  the address space, and it is pinning WAL that the active slots have long since moved past.
- The slot name embeds a different task-instance suffix (66c3bef6...) from the live one. That is consistent with a
prior DMS task that was recreated or reloaded and left its old slot behind.

We should drop vfpmcxw6... but leave the other two in place.

Next, with regard to the cutover strategy for RECAP:

The Blue/Green uses logical replication internally to keep green in sync with blue. That means the DMS slots cannot
simply be carried across. Logical slots are not copied to green, and DMS cannot use the Blue/Green replication stream as
its source.

RECAP is a CDC consumer, so if we just disable our dms instances or disable the slots, we will lose change data during
the coutover.

The risk during Blue/Green is twofold:

First, Blue/Green requires that the cluster is not being used as an external logical-replication source, so the DMS
slots have to be removed before the deployment is created.

Second, Green will have no DMS slots. Any writes between "slots removed" and "DMS re-pointed at green" would produce
change events that RECAP never sees.

I don't see a way forward with this switchover that avoids data loss without a maintenance window where the authoring
API is shut down to avoid any data changes.

Losing the change data on the lower environments (qastg and qalv) is not a big deal at all.

On prod, it's _probably_ not a big deal, either. We currently use this change to understand mutation sequences connected
to errors or change events that have caused issues for customers. It's probable that we won't need any data that is lost
during the transion, but we can't gurantee that.

So, I think we have to weigh the risk against the complexity of doing the cutover during a maintenance window.

I'm happy to discuss the plan and details during a teams call if we need to suss the details out more.

Thanks!
