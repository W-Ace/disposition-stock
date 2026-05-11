import { defineStore } from "pinia";
import { ref } from "vue";
import type { Snapshot, Bucket } from "../types";

export const useSnapshotStore = defineStore("snapshot", () => {
  const data = ref<Snapshot | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const activeBucket = ref<Bucket>("risk");

  async function load() {
    loading.value = true;
    error.value = null;
    try {
      const base = import.meta.env.BASE_URL;
      const res = await fetch(`${base}data/snapshot.json`, { cache: "no-cache" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data.value = await res.json();
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, error, activeBucket, load };
});
