/** Общие данные и утилиты для сайта и презентации */
window.SurveyApp = {
  LEVELS: ['устойчиво-позитивное', 'ситуативно-позитивное', 'ситуативно-негативное', 'устойчиво-негативное'],
  LEVEL_SHORT: ['УП', 'СП', 'СН', 'УН'],
  LEVEL_INFO: {
    'устойчиво-позитивное': {
      short: 'УП',
      title: 'Устойчиво-позитивное',
      desc: 'Позитивное отношение сформировано устойчиво: проявляется в разных ситуациях, не зависит от настроения.'
    },
    'ситуативно-позитивное': {
      short: 'СП',
      title: 'Ситуативно-позитивное',
      desc: 'Позитивное отношение есть, но проявляется не всегда — зависит от обстоятельств и настроения.'
    },
    'ситуативно-негативное': {
      short: 'СН',
      title: 'Ситуативно-негативное',
      desc: 'Негативное отношение в ряде ситуаций; в других обстоятельствах может быть нейтральным или позитивным.'
    },
    'устойчиво-негативное': {
      short: 'УН',
      title: 'Устойчиво-негативное',
      desc: 'Негативное отношение устойчиво: проявляется регулярно, трудно изменить без целенаправленной работы.'
    }
  },
  COLORS: {
    'устойчиво-позитивное': '#10b981',
    'ситуативно-позитивное': '#34d399',
    'ситуативно-негативное': '#fbbf24',
    'устойчиво-негативное': '#ef4444'
  },

  async loadData() {
    const embedded = document.getElementById('survey-data');
    if (embedded) return JSON.parse(embedded.textContent);
    const r = await fetch('data.json');
    if (!r.ok) throw new Error('data.json');
    return r.json();
  },

  classList(data) {
    return data.classes.filter(c => c !== 'Все');
  },

  scaleShort(scale) {
    return scale.replace(/^\d+\.\s*/, '').trim();
  },

  positivityIndex(scaleData) {
    const total = Object.values(scaleData).reduce((a, b) => a + b, 0);
    if (!total) return 0;
    const score =
      (scaleData['устойчиво-позитивное'] || 0) * 3 +
      (scaleData['ситуативно-позитивное'] || 0) * 2 +
      (scaleData['ситуативно-негативное'] || 0) * 1;
    return (score / (total * 3)) * 100;
  },

  posPercent(scaleData) {
    const total = Object.values(scaleData).reduce((a, b) => a + b, 0);
    if (!total) return 0;
    return ((scaleData['устойчиво-позитивное'] || 0) + (scaleData['ситуативно-позитивное'] || 0)) / total * 100;
  },

  classSize(data, cls) {
    return Object.values(data.data[cls][data.scales[0]]).reduce((a, b) => a + b, 0);
  }
};
