/*
 * uart.h
 *
 *  Created on: May 12, 2025
 *      Author: yaroslav
 */

#ifndef INC_UART_H_
#define INC_UART_H_

#include "stm32h7xx_hal.h"

void usart_Open(void);
int8_t usart_Send(char* bArray, int size_bArray);
uint16_t usart_Recv(char* bArray, uint16_t maxLength);

#endif /* INC_UART_H_ */
