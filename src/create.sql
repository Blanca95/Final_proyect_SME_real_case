SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema farmacia
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema farmacia
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `farmacia` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `farmacia` ;

-- -----------------------------------------------------
-- Table `farmacia`.`empleados`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `farmacia`.`empleados` (
  `index` BIGINT NOT NULL,
  `Vendedor` TEXT NULL DEFAULT NULL,
  INDEX `ix_Empleados_index` (`index` ASC) VISIBLE,
  PRIMARY KEY (`index`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `farmacia`.`medicamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `farmacia`.`medicamentos` (
  `index` BIGINT NOT NULL,
  `Codigo` BIGINT NULL DEFAULT NULL,
  `Denominacion` TEXT NULL DEFAULT NULL,
  `Pvp` DOUBLE NULL DEFAULT NULL,
  INDEX `ix_Medicamentos_index` (`index` ASC) VISIBLE,
  PRIMARY KEY (`index`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `farmacia`.`ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `farmacia`.`ventas` (
  `index` BIGINT NOT NULL,
  `Fecha` TEXT NULL DEFAULT NULL,
  `Hora` TEXT NULL DEFAULT NULL,
  `Organismo` TEXT NULL DEFAULT NULL,
  `Cantidad` BIGINT NULL DEFAULT NULL,
  `Pvp_facturado` DOUBLE NULL DEFAULT NULL,
  `Importe_bruto` DOUBLE NULL DEFAULT NULL,
  `Descuento` DOUBLE NULL DEFAULT NULL,
  `Importe_neto` DOUBLE NULL DEFAULT NULL,
  `Puesto` BIGINT NULL DEFAULT NULL,
  `Existencias` BIGINT NULL DEFAULT NULL,
  `Ticket` DOUBLE NULL DEFAULT NULL,
  `Familia` TEXT NULL DEFAULT NULL,
  `Mínimo` DOUBLE NULL,
  `medicamentos_index` BIGINT NOT NULL,
  `empleados_index` BIGINT NOT NULL,
  INDEX `ix_Ventas_index` (`index` ASC) VISIBLE,
  PRIMARY KEY (`index`),
  INDEX `fk_ventas_medicamentos_idx` (`medicamentos_index` ASC) VISIBLE,
  INDEX `fk_ventas_empleados1_idx` (`empleados_index` ASC) VISIBLE,
  CONSTRAINT `fk_ventas_medicamentos`
    FOREIGN KEY (`medicamentos_index`)
    REFERENCES `farmacia`.`medicamentos` (`index`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ventas_empleados1`
    FOREIGN KEY (`empleados_index`)
    REFERENCES `farmacia`.`empleados` (`index`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
