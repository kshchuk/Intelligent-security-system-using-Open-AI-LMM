/*
 * uart.c
 *
 *  Created on: May 12, 2025
 *      Author: yaroslav
 */


#include "uart.h"

#include "cmsis_os.h"

#define Q_USART2_SIZE 200

xQueueHandle g_qUsart;
osThreadId g_usart_rxTaskHandle;

extern UART_HandleTypeDef huart4;

void usart_rxTask(void);

uint8_t bGet[Q_USART2_SIZE] = {0};
uint16_t g_tail = 0;

void usart_Open(void)
{
	g_qUsart = xQueueCreate( Q_USART2_SIZE, sizeof( unsigned char ) );

	osThreadDef(usart_rxTask_NAME, usart_rxTask, osPriorityNormal, 0, Q_USART2_SIZE/4+128);
	g_usart_rxTaskHandle = osThreadCreate(osThread(usart_rxTask_NAME), NULL);

	HAL_UART_Receive_DMA(&huart4, bGet, Q_USART2_SIZE);

}

void usart_rxTask(void)
{
	for(;;)
	{
		uint16_t length = Q_USART2_SIZE - ((DMA_Stream_TypeDef*)huart4.hdmarx->Instance)->NDTR;

		while(length - g_tail)
		{
			uint8_t tmp = bGet[g_tail];
			xQueueSendToBack( g_qUsart, &tmp, 100 );
			g_tail++;
			if (g_tail == Q_USART2_SIZE)
				g_tail = 0;
		}
	}
}

int8_t usart_Send(char* bArray, int size_bArray)
{
	HAL_StatusTypeDef status;

	status = HAL_UART_Transmit_DMA(&huart4, bArray, size_bArray);

	while (HAL_UART_GetState(&huart4) != HAL_UART_STATE_READY)
	{
		if (HAL_UART_GetState(&huart4) == HAL_UART_STATE_BUSY_RX)
			break;

		osDelay(1);
	}

	if (status == HAL_OK)
		return 1;

	return 0;
}

uint16_t usart_Recv(char* bArray, uint16_t maxLength)
{
	uint8_t tmp = 0;
	uint16_t length = 0;
	while(uxQueueMessagesWaiting(g_qUsart))
	{
		xQueueReceive( g_qUsart, &tmp, 100 );
		bArray[length] = tmp;
		length++;
		if (length >= maxLength)
			break;
	}

	return length;
}
