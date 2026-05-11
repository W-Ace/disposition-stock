<script setup lang="ts">
import { computed } from "vue";
import { useSnapshotStore } from "../stores/snapshot";
import type { Bucket } from "../types";

const store = useSnapshotStore();

const tabs = computed<{ key: Bucket; label: string; count: number }[]>(() => [
  { key: "risk", label: "風險股", count: store.data?.risk.length ?? 0 },
  { key: "disposal", label: "處置中", count: store.data?.disposal.length ?? 0 },
  { key: "exiting", label: "即將出關", count: store.data?.exiting.length ?? 0 },
]);
</script>

<template>
  <nav class="tabbar">
    <button
      v-for="t in tabs"
      :key="t.key"
      :class="['tabbar__tab', { 'tabbar__tab--active': store.activeBucket === t.key }]"
      @click="store.activeBucket = t.key"
    >
      <span>{{ t.label }}</span>
      <span v-if="t.count > 0" class="tabbar__badge">{{ t.count }}</span>
    </button>
  </nav>
</template>
