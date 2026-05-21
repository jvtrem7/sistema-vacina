(function () {
  'use strict';

  var guide = document.getElementById('easyvacc-install-guide');
  if (!guide) return;

  var steps = document.getElementById('easyvacc-install-steps');
  var description = document.getElementById('easyvacc-install-description');
  var action = document.getElementById('easyvacc-install-action');
  var dismissers = guide.querySelectorAll('[data-install-dismiss]');
  var dismissKey = 'easyvacc-install-dismissed-v2';
  var deferredPrompt = null;
  var userAgent = (navigator.userAgent || '').toLowerCase();
  var isIOS = /iphone|ipad|ipod/.test(userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var isAndroid = /android/.test(userAgent);

  function dismissedThisSession() {
    try {
      return window.sessionStorage.getItem(dismissKey) === '1';
    } catch (err) {
      return false;
    }
  }

  function rememberDismissed() {
    try {
      window.sessionStorage.setItem(dismissKey, '1');
    } catch (err) {
      return;
    }
  }

  function installed() {
    return window.matchMedia('(display-mode: standalone)').matches ||
      window.matchMedia('(display-mode: fullscreen)').matches ||
      window.navigator.standalone === true;
  }

  function row(number, text) {
    return '<div class="easyvacc-install-step"><span class="easyvacc-install-step-number">' +
      number + '</span><span>' + text + '</span></div>';
  }

  function renderNativePrompt() {
    description.textContent = 'Tenha acesso direto ao painel, mesmo quando precisar trabalhar com pouca rede.';
    steps.innerHTML =
      row('1', 'Clique em Instalar EasyVacc.') +
      row('2', 'Confirme a instalação na janela do navegador.');
    action.hidden = false;
  }

  function renderIOSInstructions() {
    description.textContent = 'No iPhone ou iPad, adicione o EasyVacc pela opção do Safari.';
    steps.innerHTML =
      row('1', 'Toque em <span class="easyvacc-install-inline-icon"><i class="fa-solid fa-arrow-up-from-bracket" aria-hidden="true"></i></span> Compartilhar.') +
      row('2', 'Escolha <span class="easyvacc-install-inline-icon"><i class="fa-solid fa-square-plus" aria-hidden="true"></i></span> Adicionar à Tela de Início.') +
      row('3', 'Confirme em Adicionar.');
    action.hidden = true;
  }

  function renderAndroidInstructions() {
    description.textContent = 'Instale o EasyVacc para abrir o painel direto pela tela inicial.';
    steps.innerHTML =
      row('1', 'Abra o menu <span class="easyvacc-install-inline-icon"><i class="fa-solid fa-ellipsis-vertical" aria-hidden="true"></i></span> do navegador.') +
      row('2', 'Toque em Instalar app ou Adicionar à tela inicial.') +
      row('3', 'Confirme a instalação.');
    action.hidden = true;
  }

  function renderDesktopInstructions() {
    description.textContent = 'Instale o EasyVacc no computador para abrir o painel como aplicativo.';
    steps.innerHTML =
      row('1', 'Procure o botão Instalar na barra de endereço do navegador.') +
      row('2', 'Se ele não aparecer, abra o menu do navegador e escolha Instalar app.') +
      row('3', 'Confirme a instalação.');
    action.hidden = true;
  }

  function render() {
    if (deferredPrompt && !isIOS) {
      renderNativePrompt();
    } else if (isIOS) {
      renderIOSInstructions();
    } else if (isAndroid) {
      renderAndroidInstructions();
    } else {
      renderDesktopInstructions();
    }
  }

  function show() {
    if (installed() || dismissedThisSession()) return;
    render();
    guide.hidden = false;
    document.body.classList.add('easyvacc-install-open');
  }

  function hide(remember) {
    guide.hidden = true;
    document.body.classList.remove('easyvacc-install-open');
    if (remember) rememberDismissed();
  }

  dismissers.forEach(function (button) {
    button.addEventListener('click', function () {
      hide(true);
    });
  });

  action.addEventListener('click', function () {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.finally(function () {
      deferredPrompt = null;
      render();
    });
  });

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    if (!guide.hidden) render();
    show();
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    hide(false);
  });

  window.setTimeout(show, 350);
})();
