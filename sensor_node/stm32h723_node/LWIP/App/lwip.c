/* USER CODE BEGIN Header */
/**
 ******************************************************************************
  * File Name          : LWIP.c
  * Description        : This file provides initialization code for LWIP
  *                      middleWare.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "lwip.h"
#include "lwip/init.h"
#include "lwip/netif.h"
#if defined ( __CC_ARM )  /* MDK ARM Compiler */
#include "lwip/sio.h"
#endif /* MDK ARM Compiler */
#include "ethernetif.h"

/* USER CODE BEGIN 0 */

void logger(const char *fmt, ...) {
	printf(fmt);
}

#include "uart.h"

#include "pppos.h"
#include "sio.h"
#include "dns.h"
#include "ppp.h"

static ppp_pcb *ppp;
struct netif pppos_netif;

void PppGetTask(void const * argument)
{
  uint8_t recv[2048];
  uint16_t length = 0;
  for(;;)
  {
	length=usart_Recv(recv, 2048);
	if (length)
	{
		pppos_input(ppp, recv, length);
		logger("read - PppGetTask() len = %d\n", length);
	}

	osDelay(10);
  }

}

#include "ip4_addr.h"
#include "dns.h"

static void ppp_link_status_cb(ppp_pcb *pcb, int err_code, void *ctx)
{
		struct netif *pppif = ppp_netif(pcb);
		LWIP_UNUSED_ARG(ctx);

		switch(err_code)
		{
			case PPPERR_NONE:               /* No error. */
			{
				logger("ppp_link_status_cb: PPPERR_NONE\n\r");
				logger("   our_ip4addr = %s\n\r", ip4addr_ntoa(netif_ip4_addr(pppif)));
				logger("   his_ipaddr  = %s\n\r", ip4addr_ntoa(netif_ip4_gw(pppif)));
				logger("   netmask     = %s\n\r", ip4addr_ntoa(netif_ip4_netmask(pppif)));
			}
			break;

			case PPPERR_PARAM:             /* Invalid parameter. */
					logger("ppp_link_status_cb: PPPERR_PARAM\n");
					break;

			case PPPERR_OPEN:              /* Unable to open PPP session. */
					logger("ppp_link_status_cb: PPPERR_OPEN\n");
					break;

			case PPPERR_DEVICE:            /* Invalid I/O device for PPP. */
					logger("ppp_link_status_cb: PPPERR_DEVICE\n");
					break;

			case PPPERR_ALLOC:             /* Unable to allocate resources. */
					logger("ppp_link_status_cb: PPPERR_ALLOC\n");
					break;

			case PPPERR_USER:              /* User interrupt. */
					logger("ppp_link_status_cb: PPPERR_USER\n");
					break;

			case PPPERR_CONNECT:           /* Connection lost. */
					logger("ppp_link_status_cb: PPPERR_CONNECT\n");
					break;

			case PPPERR_AUTHFAIL:          /* Failed authentication challenge. */
					logger("ppp_link_status_cb: PPPERR_AUTHFAIL\n");
					break;

			case PPPERR_PROTOCOL:          /* Failed to meet protocol. */
					logger("ppp_link_status_cb: PPPERR_PROTOCOL\n");
					break;

			case PPPERR_PEERDEAD:          /* Connection timeout. */
					logger("ppp_link_status_cb: PPPERR_PEERDEAD\n");
					break;

			case PPPERR_IDLETIMEOUT:       /* Idle Timeout. */
					logger("ppp_link_status_cb: PPPERR_IDLETIMEOUT\n");
					break;

			case PPPERR_CONNECTTIME:       /* PPPERR_CONNECTTIME. */
					logger("ppp_link_status_cb: PPPERR_CONNECTTIME\n");
					break;

			case PPPERR_LOOPBACK:          /* Connection timeout. */
					logger("ppp_link_status_cb: PPPERR_LOOPBACK\n");
					break;
			default:
					logger("ppp_link_status_cb: unknown errCode %d\n", err_code);
					break;
		}
}

// Callback used by ppp connection
static u32_t ppp_output_cb(ppp_pcb *pcb, u8_t *data, u32_t len, void *ctx)
{
	LWIP_UNUSED_ARG(pcb);
	LWIP_UNUSED_ARG(ctx);

	if (len > 0)
	{
		if (!usart_Send(data, len))
				return 0x05;
	}
	logger("write - ppp_output_cb() len = %d\n", len);

	return len;
}

void pppConnect(void)
{
	ppp = pppos_create(&pppos_netif, ppp_output_cb, ppp_link_status_cb, NULL);
	ppp_set_default(ppp);

	osThreadId PppGetTaskHandle;
	osThreadDef(PPP_GET_TASK_NAME, PppGetTask, osPriorityNormal, 0, 128*10);
	PppGetTaskHandle = osThreadCreate(osThread(PPP_GET_TASK_NAME), NULL);

	err_t err = ppp_connect(ppp,0);
	if (err == ERR_ALREADY)
	{
		logger("Connected successfully");
	}

	for(int i=0;i<40;i++)
	{
		osDelay(500);
		if (ppp->phase >= PPP_PHASE_RUNNING)
			break;
	}

}

/* USER CODE END 0 */
/* Private function prototypes -----------------------------------------------*/
static void ethernet_link_status_updated(struct netif *netif);
/* ETH Variables initialization ----------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

/* Variables Initialization */
struct netif gnetif;
ip4_addr_t ipaddr;
ip4_addr_t netmask;
ip4_addr_t gw;
uint8_t IP_ADDRESS[4];
uint8_t NETMASK_ADDRESS[4];
uint8_t GATEWAY_ADDRESS[4];

/* USER CODE BEGIN 2 */

/* USER CODE END 2 */

/**
  * LwIP initialization function
  */
void MX_LWIP_Init(void)
{
  /* IP addresses initialization */
  IP_ADDRESS[0] = 192;
  IP_ADDRESS[1] = 168;
  IP_ADDRESS[2] = 0;
  IP_ADDRESS[3] = 123;
  NETMASK_ADDRESS[0] = 255;
  NETMASK_ADDRESS[1] = 255;
  NETMASK_ADDRESS[2] = 255;
  NETMASK_ADDRESS[3] = 0;
  GATEWAY_ADDRESS[0] = 192;
  GATEWAY_ADDRESS[1] = 168;
  GATEWAY_ADDRESS[2] = 0;
  GATEWAY_ADDRESS[3] = 1;

/* USER CODE BEGIN IP_ADDRESSES */
/* USER CODE END IP_ADDRESSES */

  /* Initialize the LwIP stack with RTOS */
  tcpip_init( NULL, NULL );

  /* IP addresses initialization without DHCP (IPv4) */
  IP4_ADDR(&ipaddr, IP_ADDRESS[0], IP_ADDRESS[1], IP_ADDRESS[2], IP_ADDRESS[3]);
  IP4_ADDR(&netmask, NETMASK_ADDRESS[0], NETMASK_ADDRESS[1] , NETMASK_ADDRESS[2], NETMASK_ADDRESS[3]);
  IP4_ADDR(&gw, GATEWAY_ADDRESS[0], GATEWAY_ADDRESS[1], GATEWAY_ADDRESS[2], GATEWAY_ADDRESS[3]);

  /* add the network interface (IPv4/IPv6) with RTOS */
  netif_add(&gnetif, &ipaddr, &netmask, &gw, NULL, &ethernetif_init, &tcpip_input);

  /* Registers the default network interface */
  netif_set_default(&gnetif);

  /* We must always bring the network interface up connection or not... */
  netif_set_up(&gnetif);

  /* Set the link callback function, this function is called on change of link status*/
  netif_set_link_callback(&gnetif, ethernet_link_status_updated);

  /* Create the Ethernet link handler thread */
/* USER CODE BEGIN H7_OS_THREAD_DEF_CREATE_CMSIS_RTOS_V1 */
  osThreadDef(EthLink, ethernet_link_thread, osPriorityBelowNormal, 0, configMINIMAL_STACK_SIZE *2);
  osThreadCreate (osThread(EthLink), &gnetif);
/* USER CODE END H7_OS_THREAD_DEF_CREATE_CMSIS_RTOS_V1 */

/* USER CODE BEGIN 3 */

  pppConnect();

/* USER CODE END 3 */
}

#ifdef USE_OBSOLETE_USER_CODE_SECTION_4
/* Kept to help code migration. (See new 4_1, 4_2... sections) */
/* Avoid to use this user section which will become obsolete. */
/* USER CODE BEGIN 4 */
/* USER CODE END 4 */
#endif

/**
  * @brief  Notify the User about the network interface config status
  * @param  netif: the network interface
  * @retval None
  */
static void ethernet_link_status_updated(struct netif *netif)
{
  if (netif_is_up(netif))
  {
/* USER CODE BEGIN 5 */
/* USER CODE END 5 */
  }
  else /* netif is down */
  {
/* USER CODE BEGIN 6 */
/* USER CODE END 6 */
  }
}

#if defined ( __CC_ARM )  /* MDK ARM Compiler */
/**
 * Opens a serial device for communication.
 *
 * @param devnum device number
 * @return handle to serial device if successful, NULL otherwise
 */
sio_fd_t sio_open(u8_t devnum)
{
  sio_fd_t sd;

/* USER CODE BEGIN 7 */
  sd = 0; // dummy code
/* USER CODE END 7 */

  return sd;
}

/**
 * Sends a single character to the serial device.
 *
 * @param c character to send
 * @param fd serial device handle
 *
 * @note This function will block until the character can be sent.
 */
void sio_send(u8_t c, sio_fd_t fd)
{
/* USER CODE BEGIN 8 */
/* USER CODE END 8 */
}

/**
 * Reads from the serial device.
 *
 * @param fd serial device handle
 * @param data pointer to data buffer for receiving
 * @param len maximum length (in bytes) of data to receive
 * @return number of bytes actually received - may be 0 if aborted by sio_read_abort
 *
 * @note This function will block until data can be received. The blocking
 * can be cancelled by calling sio_read_abort().
 */
u32_t sio_read(sio_fd_t fd, u8_t *data, u32_t len)
{
  u32_t recved_bytes;

/* USER CODE BEGIN 9 */
  recved_bytes = 0; // dummy code
/* USER CODE END 9 */
  return recved_bytes;
}

/**
 * Tries to read from the serial device. Same as sio_read but returns
 * immediately if no data is available and never blocks.
 *
 * @param fd serial device handle
 * @param data pointer to data buffer for receiving
 * @param len maximum length (in bytes) of data to receive
 * @return number of bytes actually received
 */
u32_t sio_tryread(sio_fd_t fd, u8_t *data, u32_t len)
{
  u32_t recved_bytes;

/* USER CODE BEGIN 10 */
  recved_bytes = 0; // dummy code
/* USER CODE END 10 */
  return recved_bytes;
}
#endif /* MDK ARM Compiler */

