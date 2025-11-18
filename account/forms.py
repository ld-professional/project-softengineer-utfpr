from    

class validar_cadastro(fo)

telefone_stringado= str(self.telefone)

        if telefone_stringado.count() >11:
            raise ValueError({'telefone':'O campo telefone necessita ser de 11 digitos'})