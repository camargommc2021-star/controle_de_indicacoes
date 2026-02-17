from managers.chefes_manager import get_chefes_manager

manager = get_chefes_manager()
chefes = manager.get_all_chefes()

print(f'Total de chefes: {len(chefes)}')
print()
print('Primeiros 5 chefes:')
for c in chefes[:5]:
    print(f"  {c['nome']} ({c['posto']}) - {c['funcao']}")
