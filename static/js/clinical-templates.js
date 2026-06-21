// Clinical document & note templates for Rapha (Fase 2)

const TEMPLATES_URL = '/static/clinical/templates.json';

let _cache = null;

export async function loadClinicalTemplates() {
  if (_cache) return _cache;
  const res = await fetch(TEMPLATES_URL, { cache: 'no-cache' });
  if (!res.ok) throw new Error('No se pudieron cargar las plantillas clínicas');
  _cache = await res.json();
  return _cache;
}

function _closeMenu(menu) {
  if (menu && menu.parentNode) menu.parentNode.removeChild(menu);
  document.removeEventListener('click', menu?._outsideClose, true);
}

export function showClinicalTemplateMenu(anchorEl, items, onPick) {
  if (!anchorEl || !items?.length) return;
  _closeMenu(document.querySelector('.clinical-template-menu'));

  const menu = document.createElement('div');
  menu.className = 'clinical-template-menu';
  menu.setAttribute('role', 'menu');

  const blank = document.createElement('button');
  blank.type = 'button';
  blank.className = 'clinical-template-item';
  blank.textContent = 'En blanco';
  blank.addEventListener('click', (e) => {
    e.stopPropagation();
    _closeMenu(menu);
    onPick(null);
  });
  menu.appendChild(blank);

  for (const item of items) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'clinical-template-item';
    btn.setAttribute('role', 'menuitem');
    btn.innerHTML = `<span class="clinical-template-label">${item.label}</span>`
      + (item.description ? `<span class="clinical-template-desc">${item.description}</span>` : '');
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      _closeMenu(menu);
      onPick(item);
    });
    menu.appendChild(btn);
  }

  const rect = anchorEl.getBoundingClientRect();
  menu.style.position = 'fixed';
  menu.style.top = `${rect.bottom + 4}px`;
  menu.style.left = `${Math.max(8, rect.left - 120)}px`;
  menu.style.zIndex = '10050';
  document.body.appendChild(menu);

  menu._outsideClose = (ev) => {
    if (!menu.contains(ev.target) && ev.target !== anchorEl) _closeMenu(menu);
  };
  requestAnimationFrame(() => document.addEventListener('click', menu._outsideClose, true));
}

export async function pickDocumentTemplate(anchorEl) {
  const data = await loadClinicalTemplates();
  return new Promise((resolve) => {
    showClinicalTemplateMenu(anchorEl, data.documents || [], (tpl) => resolve(tpl));
  });
}

export async function pickNoteTemplate(anchorEl) {
  const data = await loadClinicalTemplates();
  return new Promise((resolve) => {
    showClinicalTemplateMenu(anchorEl, data.notes || [], (tpl) => resolve(tpl));
  });
}

const ClinicalTemplates = {
  loadClinicalTemplates,
  showClinicalTemplateMenu,
  pickDocumentTemplate,
  pickNoteTemplate,
};

export default ClinicalTemplates;
