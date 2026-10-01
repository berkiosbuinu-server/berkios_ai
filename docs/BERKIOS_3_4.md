# Berkios 3.4 — Change / Verify / Repair Cycle

Berkios 3.4 introduit un cycle concret de modification.

## Cycle

`start`
  -> `propose`
  -> `apply`
  -> `verify`
  -> `complete`

Si la vérification échoue :

`verify`
  -> `repair_required`
  -> `propose_repair`

## Engines

`ChangeCycle` accepte par injection :
- ChangeEngine
- VerificationEngine
- Permission manager
- Run Memory

L'orchestrateur reste découplé des implémentations concrètes.

## Important

Une réparation n'est pas appliquée automatiquement dans cette version.
Berkios produit une demande structurée de réparation afin que le futur
agent puisse analyser l'erreur, préparer une nouvelle proposition et
respecter les contrôles de permission/revue.

## Suite

La prochaine évolution peut connecter `ProviderEngine` à ce cycle afin
que les décisions de proposition et de réparation soient générées par
le provider sélectionné, puis enrichies par Error Intelligence et
Correction Memory.
