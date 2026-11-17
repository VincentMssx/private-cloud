<?php
script('familytri', 'review');
style('familytri', 'review');
$url = $_['url'];
?>
<main class="tri" id="family-review" data-ignore="<?php p($url->linkToRoute('familytri.page.ignore')); ?>">
<h1>Trier mes photos</h1>
<form method="get"><label>Année <select name="year"><option value="">Toutes</option>
<?php foreach ($_['years'] as $year): ?><option <?php if ($year === $_['year']) echo 'selected'; ?>><?php p($year); ?></option><?php endforeach; ?>
</select></label> <button>Afficher</button></form>
<p role="status" id="tri-status"></p>
<?php if (!$_['count']): ?><p>Aucune suggestion pour le moment. Les nouvelles photos sont analysées en arrière-plan.</p><?php endif; ?>
<?php foreach ($_['groups'] as $key => $group):
    $single = count($group['items']) === 1; ?>
<section class="serie" data-key="<?php p($key); ?>">
<h2><?php p($single ? 'Vérifier la netteté' : 'Comparer la série'); ?> · <?php p(substr($group['items'][0]['datetaken'],0,10)); ?></h2>
<p><?php p($single ? 'Les contours semblent peu détaillés. Vérifiez la photo avant de décider.' :
'Les cadrages se ressemblent et les dates sont espacées de moins de deux minutes.'); ?></p>
<?php if (!$single && !$group['best']): ?><p>Qualité trop proche pour départager les clichés.</p><?php endif; ?>
<div class="photos">
<?php foreach ($group['items'] as $photo):
    $preview = $url->linkToRoute('core.Preview.getPreviewByFileId', ['fileId'=>$photo['fileid'],'x'=>512,'y'=>512,'a'=>1]);
    $path = substr($photo['path'],6);
    $dav = $url->getAbsoluteURL('/remote.php/dav/files/'.rawurlencode($_['uid']).'/'.implode('/',array_map('rawurlencode',explode('/',$path))));
?>
<figure><a href="<?php p($url->linkToRoute('files.view.showFile',['fileid'=>$photo['fileid']])); ?>"><img loading="lazy" alt="<?php p(basename($path)); ?>" src="<?php p($preview); ?>"></a>
<figcaption><strong><?php p(basename($path)); ?></strong>
<?php if ($group['best'] === $photo['fileid']): ?><p>À conserver en priorité selon la netteté et l’exposition mesurées.</p><?php endif; ?>
<p><?php p($photo['sharp'] < \OCA\FamilyTri\Service\Suggestions::LOW_SHARPNESS ? 'Flou possible' : 'Contours marqués'); ?> · <?php p(round(100*$photo['clipped'])); ?> % de pixels très sombres ou très clairs</p>
<label><input type="checkbox" data-url="<?php p($dav); ?>" data-etag="<?php p($photo['etag']); ?>"> Mettre à la corbeille</label></figcaption></figure>
<?php endforeach; ?></div>
<div class="actions"><button type="button" class="discard" disabled>Confirmer la sélection</button>
<button type="button" class="ignore">Ignorer cette suggestion</button></div>
</section><?php endforeach; ?>
<?php if ($_['count'] > 24): ?><p>24 suggestions affichées sur <?php p($_['count']); ?>. Les suivantes apparaîtront après vos décisions.</p><?php endif; ?>
</main>
