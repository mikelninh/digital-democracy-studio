(()=>{
  const blocks=[...document.querySelectorAll('[data-analyst-decision]')];
  if(!blocks.length)return;

  blocks.forEach(block=>{
    const targetSelector=block.dataset.revealTarget;
    const target=targetSelector?document.querySelector(targetSelector):null;
    const feedback=block.querySelector('[data-decision-feedback]');
    const reveal=block.querySelector('[data-reveal-assessment]');
    const skip=block.querySelector('[data-skip-decision]');
    const choices=[...block.querySelectorAll('[data-choice]')];

    // Progressive enhancement: without JS the assessment remains visible.
    if(target)target.hidden=true;
    if(reveal)reveal.hidden=true;

    function showAssessment(){
      if(target){
        target.hidden=false;
        target.scrollIntoView({behavior:'smooth',block:'start'});
      }
      if(reveal)reveal.hidden=true;
      block.classList.add('decision-complete');
    }

    choices.forEach(choice=>choice.addEventListener('click',()=>{
      if(block.classList.contains('answered'))return;
      block.classList.add('answered');
      const correct=choice.dataset.correct==='true';
      choices.forEach(btn=>{
        btn.disabled=true;
        if(btn.dataset.correct==='true')btn.classList.add('is-correct');
      });
      choice.classList.add('is-selected');
      if(!correct)choice.classList.add('is-wrong');
      if(feedback){
        feedback.hidden=false;
        feedback.className='decision-feedback '+(correct?'correct':'wrong');
        feedback.innerHTML=`<strong>${correct?'Good call.':'Useful trap.'}</strong><span>${correct?block.dataset.correctFeedback:block.dataset.wrongFeedback}</span>`;
      }
      if(reveal)reveal.hidden=false;
    }));

    reveal?.addEventListener('click',showAssessment);
    skip?.addEventListener('click',showAssessment);
  });
})();
