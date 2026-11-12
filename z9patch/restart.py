"""Authored gate; the displaced word is supplied by the hash-checked local input."""
def ordinary_restart_assembly(displaced_word):
    if type(displaced_word)is not int or not 0<=displaced_word<1<<32:
        raise ValueError('A single locally read instruction is required')
    pairs=[(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15),(16,17),(18,30)]
    save=['sub sp,sp,#176']+[f'stp x{i},x{j},[sp,#{i*8}]'for i,j in pairs]
    restore=['ldr x9,[sp,#168]','msr nzcv,x9']+[f'ldp x{i},x{j},[sp,#{i*8}]'for i,j in pairs]+['add sp,sp,#176']
    return ['.global hook_ordinary_restart','hook_ordinary_restart:',*save,
            'mrs x9,nzcv','str x9,[sp,#168]','bl m2_ordinary_restart_required',
            'cbnz w0,ordinary_custom_restart',*restore,f'.inst {displaced_word}',
            'b ordinary_restart_continue','ordinary_custom_restart:',*restore,
            'b ordinary_restart_stop_native']
