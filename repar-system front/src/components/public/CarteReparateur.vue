<script setup>
defineProps({ person: { type: Object, required: true }, search: Boolean })
</script>

<template>
  <article class="pro-card">
    <div class="photo" :style="{ backgroundImage: `url(${person.image})` }">
      <span v-if="person.badge" class="badge">{{ person.badge }}</span>
    </div>
    <div class="card-content">
      <div class="name-score"><h3>{{ person.name }}</h3><strong><i>★</i> {{ person.score === '—' ? 'Nouveau' : person.score }}</strong></div>
      <p class="company">{{ person.company }} · {{ person.specialty }}</p>
      <p class="location"><span>⌖</span> {{ person.location }}</p>
      <div v-if="person.tags?.length" class="tags"><span v-for="tag in person.tags.slice(0, 3)" :key="tag">{{ tag }}</span></div>
      <RouterLink class="profile-button" :to="`/reparateurs/${person.slug}`">Voir le profil</RouterLink>
    </div>
  </article>
</template>

<style scoped>
.pro-card{overflow:hidden;border:1px solid #e4e9f0;border-radius:13px;background:#fff;box-shadow:0 3px 12px #143d6a0d;transition:transform .18s ease,box-shadow .18s ease}.pro-card:hover{transform:translateY(-3px);box-shadow:0 10px 24px #143d6a20}.photo{position:relative;height:178px;background:#eaf0f7 center/cover no-repeat}.badge{position:absolute;top:12px;right:12px;border-radius:14px;background:#0873f7;color:#fff;padding:5px 9px;font-size:8px;font-weight:800;letter-spacing:.2px}.card-content{padding:14px 15px 16px}.name-score{display:flex;align-items:center;justify-content:space-between;gap:8px}.name-score h3{overflow:hidden;margin:0;color:#102a52;font-size:15px;line-height:1.25;text-overflow:ellipsis;white-space:nowrap}.name-score strong{flex:none;color:#213a5d;font-size:11px}.name-score i{color:#ffbf22;font-style:normal;font-size:14px}.company,.location{overflow:hidden;margin:6px 0 0;color:#74839a;font-size:10px;text-overflow:ellipsis;white-space:nowrap}.location{margin-top:10px;color:#8a98ab}.location span{color:#4f84cd;font-size:12px}.tags{display:flex;min-height:26px;gap:5px;overflow:hidden;margin-top:12px}.tags span{display:block;overflow:hidden;max-width:100%;border-radius:4px;background:#f0f4f8;color:#64758b;padding:5px 7px;font-size:7px;font-weight:800;text-overflow:ellipsis;white-space:nowrap}.profile-button{display:grid;place-items:center;width:100%;height:37px;margin-top:14px;border-radius:7px;background:#06275b;color:#fff;font-size:10px;font-weight:800;transition:background .18s}.profile-button:hover{background:#087f70}@media(max-width:800px){.photo{height:210px}.card-content{padding:16px}.name-score h3{font-size:16px}}</style>
