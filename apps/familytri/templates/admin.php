<?php
use OCP\Util;
script('familytri', 'admin');
style('familytri', 'admin');
?>
<section class="section" id="family-admin">
<h2>Espaces familiaux</h2>
<?php if ($_['free'] !== false && $_['capacity'] !== false): ?>
<p>Volume de données du serveur · <?php p(Util::humanFileSize($_['free'])); ?> libres sur <?php p(Util::humanFileSize($_['capacity'])); ?>.</p>
<?php endif; ?>
<p>Dernière sauvegarde vérifiée · <?php p($_['lastBackup'] ?: 'Aucune sauvegarde enregistrée'); ?></p>
<p>Les originaux actifs et la corbeille sont comptés séparément. La file d’analyse concerne les photos déjà indexées par Memories. Les erreurs sont réessayées en arrière-plan.</p>
<div class="family-grid">
<?php foreach ($_['accounts'] as $a): ?>
<article class="family-account" data-user="<?php p($a['uid']); ?>">
<h3><?php p($a['name']); ?></h3><?php if ($a['name'] !== $a['uid']): ?><small><?php p($a['uid']); ?></small><?php endif; ?>
<dl>
<?php foreach (['used'=>'Volume actif', 'quota'=>'Quota effectif', 'files'=>'Fichiers', 'photos'=>'Dont photos', 'trash'=>'Corbeille', 'pending'=>'Analyses en attente', 'failed'=>'Analyses en erreur'] as $key=>$label): ?>
<div><dt><?php p($label); ?></dt><dd data-metric="<?php p($key); ?>"><?php
    if (in_array($key, ['used', 'trash'], true)) { p(Util::humanFileSize($a[$key])); }
    elseif ($key === 'quota' && $a[$key] === 'none') { p('Sans limite'); }
    else { p($a[$key]); }
?></dd></div>
<?php endforeach; ?>
</dl>
<details><summary>Modifier le quota</summary>
<form action="<?php p($_['quotaUrl']); ?>" method="post" class="family-quota">
<input type="hidden" name="uid" value="<?php p($a['uid']); ?>">
<label>Limite <input type="number" name="amount" min="1" max="9999999" step="1" required></label>
<label>Unité <select name="unit"><option value="GB">Gio</option><option value="MB">Mio</option><option value="default">Quota par défaut</option></select></label>
<button type="submit">Enregistrer</button>
</form></details>
<p class="family-status" role="status"></p>
</article>
<?php endforeach; ?>
</div></section>
