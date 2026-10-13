<script setup>
defineProps({ person: { type: Object, required: true }, search: Boolean })

const iconForTag = (tag) => {
  const label = tag.toLocaleLowerCase()
  if (label.includes('téléph') || label.includes('smartphone') || label.includes('tablette')) return 'smartphone'
  if (label.includes('informatique') || label.includes('ordinateur')) return 'computer'
  if (label.includes('climatisation')) return 'climate'
  if (label.includes('télé') || label.includes('tv')) return 'television'
  if (label.includes('électronique')) return 'wrench'
  return 'wrench'
}
</script>

<template>
  <article class="pro-card">
    <div class="photo" :style="{ backgroundImage: `url(${person.image})` }">
      <span v-if="person.verified" class="badge"><AppIcon name="check" :size="11" /> Vérifié</span>
    </div>
    <div class="card-content">
      <div class="name-score"><h3>{{ person.name }}</h3><span v-if="person.availability" class="availability"><i></i>{{ person.availability }}</span></div>
      <p class="rating" :class="{ 'rating-new': person.score === '—' }"><AppIcon name="star" :size="14" fill="currentColor" /> <strong>{{ person.score === '—' ? 'Nouveau réparateur' : person.score }}</strong><span v-if="person.score !== '—'"> · {{ person.nombreAvis || 0 }} avis</span></p>
      <p class="location"><AppIcon name="pin" :size="13" /> {{ person.location }}</p>
      <div v-if="person.tags?.length" class="tags"><span v-for="tag in person.tags.slice(0, 3)" :key="tag"><AppIcon :name="iconForTag(tag)" :size="14" />{{ tag }}</span></div>
      <RouterLink class="profile-button" :to="`/reparateurs/${person.slug}`">Voir le profil <span aria-hidden="true">→</span></RouterLink>
    </div>
  </article>
</template>

<style scoped>
.pro-card{overflow:hidden;border:1px solid #d2e2e4;border-radius:12px;background:#fff;box-shadow:none;transition:transform .18s ease}.pro-card:hover{transform:translateY(-3px);box-shadow:none}.photo{position:relative;height:156px;background:#edf6f3 center/cover no-repeat}.badge{position:absolute;top:12px;right:12px;display:inline-flex;align-items:center;gap:5px;border:1px solid rgba(255,255,255,.7);border-radius:16px;background:#f0fbf8;color:#087f70;padding:6px 11px;font-size:10px;font-weight:800}.card-content{padding:13px 15px 14px}.name-score{display:flex;align-items:center;justify-content:space-between;gap:8px}.name-score h3{overflow:hidden;margin:0;color:#102f43;font-size:18px;line-height:1.25;text-overflow:ellipsis;white-space:nowrap}.availability{display:flex;align-items:center;gap:7px;flex:none;color:#087f70;font-size:11px;font-weight:600}.availability i{width:7px;height:7px;border-radius:50%;background:#0c927d}.rating{display:flex;align-items:center;gap:4px;margin:5px 0 0;color:#506b7d;font-size:11px}.rating :deep(svg){color:#f2ae16}.rating strong{color:#18384b;font-weight:700}.rating-new :deep(svg){color:#9aaeb3}.location{display:flex;align-items:center;gap:5px;overflow:hidden;margin:10px 0 0;color:#587286;font-size:11px;text-overflow:ellipsis;white-space:nowrap}.location :deep(svg){flex:none;color:#078878}.tags{display:flex;min-height:28px;gap:8px;overflow:hidden;margin-top:12px}.tags span{display:inline-flex;align-items:center;gap:6px;overflow:hidden;max-width:100%;border:1px solid transparent;border-radius:999px;background:#edf7f5;color:#075e5b;padding:7px 10px;font-size:10px;font-weight:600;text-overflow:ellipsis;white-space:nowrap}.tags span :deep(svg){flex:none;color:#087f70}.profile-button{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;height:39px;margin-top:13px;border:1px solid #d8e0e3;border-radius:8px;background:#fff;color:#34454b}.profile-button:hover{border-color:#c7d0d3;background:#f3f5f5;color:#25363c}@media(max-width:800px){.photo{height:180px}.card-content{padding:14px}.name-score h3{font-size:16px}}</style>
