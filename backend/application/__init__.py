"""Application layer.

Sits above the domain aggregates. Holds cross-aggregate query services and the
read models they assemble — the explicit equivalent of GraphQL field resolvers.
Each repository still resolves only its own aggregate by id; this layer is the
only place that knows about more than one aggregate at a time.
"""
